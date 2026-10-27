import base64
import json
import pickle
import re
import urllib.parse
from concurrent.futures import ThreadPoolExecutor

from bs4 import BeautifulSoup
from resources.lib.endpoints import malsync
from resources.lib.ui import client, control, database, source_utils, utils
from resources.lib.ui.BrowserBase import BrowserBase
from resources.lib.ui.megaplay_extractor import extract_megaplay_sources


class Sources(BrowserBase):
    _BASE_URL = 'https://9anime.me.uk/'
    _HEADERS = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Referer': 'https://9anime.me.uk/',
    }

    def get_sources(self, mal_id, episode):
        control.log(f"9Anime: Getting sources for MAL ID {mal_id}, Episode {episode}")
        show = database.get_show(mal_id)
        if not show:
            return []

        kodi_meta = pickle.loads(show.get('kodi_meta'))
        title = self._clean_title(kodi_meta.get('name') or '')

        try:
            target_ep = int(episode)
        except (TypeError, ValueError):
            control.log(f"9Anime: Invalid episode number: {episode}")
            return []

        keywords = self._search_keywords(kodi_meta, mal_id)
        series_url, matched_title = self._find_series_url(keywords)
        if not series_url:
            control.log(f"9Anime: No series found for '{title}'")
            return []

        control.log(f"9Anime: Matched series '{matched_title}' -> {series_url}")
        ep_page_url, is_dub = self._find_episode_url(series_url, target_ep)
        if not ep_page_url:
            control.log(f"9Anime: Episode {target_ep} not found in {series_url}")
            return []

        control.log(f"9Anime: Found episode page: {ep_page_url}")
        mirrors = self._get_episode_mirrors(ep_page_url)
        if not mirrors:
            control.log(f"9Anime: No mirrors found on {ep_page_url}")
            return []

        # Filter by sub/dub preference if applicable
        pref = control.getInt('general.source')
        # 1 = sub only, 2 = dub only
        if pref == 1 and is_dub:
            control.log("9Anime: User requested SUB only, skipping DUB source")
            return []
        elif pref == 2 and not is_dub:
            control.log("9Anime: User requested DUB only, skipping SUB source")
            return []

        lang = 3 if is_dub else 2
        tasks = [(label, embed_url, title, target_ep, lang) for label, embed_url in mirrors]

        results = utils.parallel_process(tasks, self._extract_mirror_worker)
        sources = [src for src in results if src]
        control.log(f"9Anime: Returning {len(sources)} source(s)")
        return sources

    def _search_keywords(self, kodi_meta, mal_id):
        keywords = []
        seen = set()

        def add(val):
            val = (val or '').strip()
            key = val.lower()
            if val and key not in seen:
                seen.add(key)
                keywords.append(val)

        # English title is usually the primary title on 9anime.me.uk
        add(kodi_meta.get('ename'))
        add(kodi_meta.get('name'))
        add(kodi_meta.get('title'))

        # Also add main title part before colons
        name = kodi_meta.get('name') or ''
        if ':' in name:
            add(name.split(':', 1)[0].strip())
        ename = kodi_meta.get('ename') or ''
        if ':' in ename:
            add(ename.split(':', 1)[0].strip())

        # MAL Sync mapping titles
        for site in ('Zoro', 'Gogoanime', 'animepahe'):
            try:
                add(malsync.get_title(mal_id, site=site))
            except Exception:
                pass

        return keywords

    def _find_series_url(self, keywords):
        for query in keywords:
            search_url = f"{self._BASE_URL}?s={urllib.parse.quote_plus(query)}"
            html = database.get(self._get_request, 8, search_url, headers=self._HEADERS)
            if not html:
                continue

            soup = BeautifulSoup(html, 'html.parser')
            articles = soup.find_all('article', class_='bs')
            if not articles:
                continue

            # Return the first matching series link
            for art in articles:
                a = art.find('a', itemprop='url')
                if a and a.get('href'):
                    return a.get('href'), a.get('title') or a.text.strip()
        return None, None

    def _find_episode_url(self, series_url, target_ep):
        html = database.get(self._get_request, 8, series_url, headers=self._HEADERS)
        if not html:
            return None, False

        soup = BeautifulSoup(html, 'html.parser')
        eplister = soup.find('div', class_='eplister')
        if not eplister:
            return None, False

        for li in eplister.find_all('li'):
            num_el = li.find(class_='epl-num')
            if num_el:
                m = re.search(r'\d+', num_el.text)
                if m and int(m.group(0)) == target_ep:
                    a = li.find('a')
                    if a and a.get('href'):
                        href = a.get('href')
                        is_dub = 'dub' in href.lower() or 'dub' in (num_el.text or '').lower()
                        return href, is_dub

        return None, False

    def _get_episode_mirrors(self, ep_url):
        html = database.get(self._get_request, 8, ep_url, headers=self._HEADERS)
        if not html:
            return []

        soup = BeautifulSoup(html, 'html.parser')
        mirrors = []
        sel = soup.find('select', class_='mirror')
        if sel:
            for opt in sel.find_all('option'):
                val = opt.get('value', '').strip()
                if val:
                    try:
                        decoded = base64.b64decode(val).decode('utf-8', errors='ignore')
                        m = re.search(r'src=["\']([^"\']+)["\']', decoded)
                        if m:
                            mirrors.append((opt.text.strip(), m.group(1)))
                    except Exception:
                        pass

        if not mirrors:
            iframe = soup.find('iframe')
            if iframe and (iframe.get('src') or iframe.get('data-src')):
                mirrors.append(('Default', iframe.get('src') or iframe.get('data-src')))

        return mirrors

    def _extract_mirror_worker(self, task):
        label, embed_url, title, episode, lang = task
        try:
            if '1anime.site' in embed_url:
                # Direct MP4 embed
                html_1a = database.get(self._get_request, 8, embed_url, headers={'Referer': self._BASE_URL})
                if html_1a:
                    m_src = re.search(r'<source\s+src=["\']([^"\']+)["\']', html_1a)
                    if m_src:
                        direct_url = m_src.group(1) + '|Referer=https://my.1anime.site/'
                        return {
                            'release_title': f"{title} - Ep {episode}",
                            'hash': direct_url,
                            'type': 'direct',
                            'quality': 3,  # 1080p
                            'debrid_provider': '',
                            'provider': '9anime',
                            'size': 'NA',
                            'seeders': 0,
                            'byte_size': 0,
                            'info': ['1Anime (MP4)' + (' DUB' if lang == 3 else ' SUB')],
                            'lang': lang,
                            'channel': 2,
                            'sub': 1,
                        }

            elif 'megaplay.buzz' in embed_url:
                # Direct HLS stream with multi-subtitles
                res = extract_megaplay_sources(embed_url, referer=self._BASE_URL)
                if res and res.get('sources'):
                    srclink = res['sources'][0].get('file')
                    if srclink:
                        subs = []
                        sub_headers = {
                            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                            'Referer': 'https://megaplay.buzz/',
                        }
                        for idx, track in enumerate(res.get('tracks') or []):
                            if track.get('kind') == 'captions' and track.get('file'):
                                track_label = track.get('label') or ''
                                subs.append({
                                    'url': track.get('file'),
                                    'lang': track_label,
                                    'name': track_label,
                                    'index': idx,
                                    'headers': sub_headers,
                                })

                        skip = {}
                        intro = res.get('intro') or {}
                        outro = res.get('outro') or {}
                        if intro.get('end') and int(intro.get('end', 0)) > 0:
                            skip['intro'] = intro
                        if outro.get('end') and int(outro.get('end', 0)) > 0:
                            skip['outro'] = outro

                        netloc = urllib.parse.urljoin(embed_url, '/')
                        headers = {'Referer': netloc, 'Origin': netloc.rstrip('/')}
                        hls_url = f"{srclink}|User-Agent=Mozilla/5.0&{urllib.parse.urlencode(headers)}"

                        source = {
                            'release_title': f"{title} - Ep {episode}",
                            'hash': hls_url,
                            'type': 'direct',
                            'quality': 3,  # 1080p master HLS
                            'debrid_provider': '',
                            'provider': '9anime',
                            'size': 'NA',
                            'seeders': 0,
                            'byte_size': 0,
                            'info': ['MegaPlay (HLS)' + (' DUB' if lang == 3 else ' SUB')],
                            'lang': lang,
                            'channel': 3,
                            'sub': 1,
                        }
                        if subs:
                            source['subs'] = subs
                        if skip:
                            source['skip'] = skip
                        return source

            else:
                # Fallback to embed extractor for standard third-party hosts
                host = source_utils.get_embedhost(embed_url) or label
                return {
                    'release_title': f"{title} - Ep {episode}",
                    'hash': embed_url,
                    'type': 'embed',
                    'quality': 2,
                    'debrid_provider': '',
                    'provider': '9anime',
                    'size': 'NA',
                    'seeders': 0,
                    'byte_size': 0,
                    'info': [host + (' DUB' if lang == 3 else ' SUB')],
                    'lang': lang,
                    'channel': 3,
                    'sub': 1,
                }
        except Exception as e:
            control.log(f"9Anime: Failed to extract mirror {label}: {e}", level='warning')

        return None
