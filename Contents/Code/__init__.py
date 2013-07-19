import random

PREFIX          = "/video/hulu" 

TITLE           = 'Hulu'
ART             = 'art-default.jpg'
ICON_DEFAULT    = 'icon-default.png'
ICON_SEARCH     = 'icon-search.png'
ICON_PREFS      = 'icon-prefs.png'

URL_LISTINGS      = 'http://www.hulu.com/browse/search?keyword=&alphabet=All&family_friendly=0&closed_captioned=0&channel=%s&subchannel=&network=All&display=%s&decade=All&type=%s&view_as_thumbnail=true&block_num=%s'
EPISODE_LISTINGS  = 'http://www.hulu.com/videos/slider?classic_sort=asc&items_per_page=%d&season=%d&show_id=%s&show_placeholders=1&sort=original_premiere_date&type=episode'
URL_QUEUE         = 'http://www.hulu.com/profile/queue?view=list&kind=thumbs&order=asc&page=%d&sort=position'

# The URL below is a json for getting any type of sort results for all types of movies and shows. 
# The %s arguments for url below are main_type, section, sort, items_per_page, position, and access token
#USING NOW
HuluJson = 'http://www.hulu.com/mozart/v1.h2o/%s/%s?exclude_hulu_content=1&sort=%s&items_per_page=32&position=%s&_user_pgid=1&_content_pgid=195&_device_id=1&access_token=%s'

# The URL below is a specific json for getting all videos associated with shows so they do not have to be separated into episodes and clips.
# The %s arguments are with sort, position, token. 
# USING NOW
HuluShowJson = 'http://www.hulu.com/mozart/v1.h2o/shows?exclude_hulu_content=1&sort=%s&items_per_page=32&position=%s&_user_pgid=1&_content_pgid=195&_device_id=1&access_token=%s'

# This below is a json for getting specific videos whether clips or episodes for shows 
# The %s arguments are show_id, section, show_id, sort, section, position, access_token. And add &season_number= to end for season episodes
# USING NOW
HuluVidJSON = 'http://www.hulu.com/mozart/v1.h2o/shows/%s/%ss?include_nonbrowseable=1&show_id=%s&sort=%s&video_type=%s&items_per_page=32&position=%s&access_token=%s'

# Added these three variables for URL completion
HuluVidURL = 'http://www.hulu.com/watch/'
HuluShowURL = 'http://www.hulu.com/show/'
HuluURL = 'http://www.hulu.com/'

REGEX_CHANNEL_LISTINGS      = Regex('Element.replace\("channel", "(.+)\);')
REGEX_SHOW_LISTINGS         = Regex('Element.(update|replace)\("(show_list|browse-lazy-load)", "(?P<content>.+)\);')
REGEX_RECOMMENDED_LISTINGS  = Regex('Element.update\("rec-hub-main", "(.+)\);')
REGEX_RATING_FEED           = Regex('Rating: ([^ ]+) .+')
REGEX_TV_EPISODE_FEED       = Regex('(?P<show>[^-]+) - s(?P<season>[0-9]+) \| e(?P<episode>[0-9]+) - (?P<title>.+)$')
REGEX_TV_EPISODE_LISTING    = Regex('Season (?P<season>[0-9]+) : Ep. (?P<episode>[0-9]+).*\(((?P<hours>[0-9])+:)?(?P<mins>[0-9]+):(?P<secs>[0-9]+)\)', Regex.DOTALL)
REGEX_TV_EPISODE_EMBED      = Regex('Season (?P<season>[0-9]+)\s+.+')
REGEX_TV_EPISODE_QUEUE      = Regex('S(?P<season>[0-9]+) : Ep\. (?P<episode>[0-9]+)')
# The Hulu feeds no longer exists. The only feed still available is the episode feed at  'http://www.hulu.com/feed/show/%s/episodes' where %s is show_id

# Added two RegEx for pulling ids needed for JSON
RE_HULU_TOKEN = Regex("API_DONUT = '(.+?)';")
RE_HULU_ID = Regex('var rawData = {"id": (.+?), "name":')

NAMESPACES      = {'activity': 'http://activitystrea.ms/spec/1.0/',
                   'media': 'http://search.yahoo.com/mrss/'}

####################################################################################################
def Start():
  Plugin.AddPrefixHandler(PREFIX, MainMenu, TITLE, ICON_DEFAULT, ART)
  Plugin.AddViewGroup('InfoList', viewMode = 'InfoList', mediaType = 'items')
  Plugin.AddViewGroup('List', viewMode = 'List', mediaType = 'items')

  ObjectContainer.title1 = TITLE
  ObjectContainer.art = R(ART)
  ObjectContainer.view_group = 'List'

  DirectoryObject.thumb = R(ICON_DEFAULT)
  DirectoryObject.art = R(ART)
  
  VideoClipObject.thumb = R(ICON_DEFAULT)
  VideoClipObject.art = R(ART)

  HTTP.CacheTime = CACHE_1HOUR
  HTTP.Headers['User-Agent'] = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.7; rv:12.0) Gecko/20100101 Firefox/12.0'

  loginResult = HuluLogin()
  Log("Login success: " + str(loginResult))
        
####################################################################################################  
def HuluLogin():

  username = Prefs["email"]
  password = Prefs["password"]

  if (username != None) and (password != None):
    authentication_url = "https://secure.hulu.com/account/authenticate?" + str(int(random.random()*1000000000))
    authentication_headers = {"Cookie": "sli=1; login=" + username + "; password=" + password + ";"}
    resp = HTTP.Request(authentication_url, headers = authentication_headers, cacheTime=0).content
    
    if resp == "Login.onComplete();":
      HTTP.Headers['Cookie'] = HTTP.CookiesForURL('https://secure.hulu.com/')
      for item in HTTP.CookiesForURL('https://secure.hulu.com/').split(';'):
        if '_hulu_uid' in item :
          Dict['_hulu_uid'] = item[11:]
      return True
    else:
      return False
  else:
    return False
        
####################################################################################################
def MainMenu():
  oc = ObjectContainer()
  oc.add(DirectoryObject(key = Callback(MyHulu, title = "My Hulu"), title = "My Hulu"))
  oc.add(DirectoryObject(key = Callback(Channels, title = "TV", item_type = "tv", display = "Shows%20with%20full%20episodes%20only"), title = "TV"))
  oc.add(DirectoryObject(key = Callback(Channels, title = "Movies", item_type = "movies", display = "Full%20length%20movies%20only"), title = "Movies"))
  oc.add(DirectoryObject(key = Callback(MostPopular, title = "Most Popular"), title = "Most Popular"))
  oc.add(DirectoryObject(key = Callback(MostRecent, title = "Recently Added"), title = "Recently Added"))
  oc.add(DirectoryObject(key = Callback(UserRating, title = "By User Rating"), title = "By User Rating"))
  oc.add(DirectoryObject(key = Callback(SoonExpire, title = "Soon-to-Expire", title = "Soon-to-Expire Videos"))
  oc.add(SearchDirectoryObject(identifier="com.plexapp.plugins.hulu", title = "Search...", prompt = "Search for Videos", thumb = R(ICON_SEARCH)))
  oc.add(PrefsObject(title = 'Preferences', thumb = R(ICON_PREFS)))
  return oc

####################################################################################################
def MyHulu(title):

  # Attempt to login
  loginResult = HuluLogin()  
  Log("MyHulu Login success: " + str(loginResult))

  if loginResult:
    oc = ObjectContainer()
    oc.add(DirectoryObject(key = Callback(Queue, title = "My Queue"), title = "My Queue"))
    oc.add(DirectoryObject(key = Callback(Recommended, title = "TV Show Recommendations", url = "http://www.hulu.com/recommendation/search?closed_captioned=0&video_type=TV"), title = "TV Show Recommendations"))
    oc.add(DirectoryObject(key = Callback(Recommended, title = "Movie Recommendations", url = "http://www.hulu.com/recommendation/search?closed_captioned=0&video_type=Movie"), title = "Movie Recommendations"))
    oc.add(DirectoryObject(key = Callback(Favorites, title = "My Favorites"), title = "My Favorites"))
  else:
    oc = MessageContainer("User info required", "Please enter your Hulu email address and password in Preferences.")
  return oc
  
####################################################################################################
@route('/video/hulu/channels')
def Channels(title, item_type, display):

  oc = ObjectContainer(title2 = title)
  channels_page = HTTP.Request(URL_LISTINGS % ("All", display, item_type, 0)).content
  html_content = REGEX_CHANNEL_LISTINGS.findall(channels_page)[0].decode('unicode_escape')
  html_page = HTML.ElementFromString(html_content)

  for genre in html_page.xpath('//div[@class="cbx-options"]//li'):
    channel = genre.get('value')
    oc.add(DirectoryObject(
      key = Callback(ListShows, title = channel, channel = channel, item_type = item_type, display = display),
      title = channel))

  return oc

####################################################################################################
def UserRating(title):
  oc = ObjectContainer(title2 = title)
  oc.add(DirectoryObject(key = Callback(ShowListSort, title = "Shows By User Rating", sort='user_rating'), title = "Shows By User Rating"))
  oc.add(DirectoryObject(key = Callback(MovieSections, title = "Movies By User Rating", sort='user_rating'), title = "Movies By User Rating"))
  return oc
####################################################################################################
# Can't do videos need a feed for that and feed gone
def SoonExpire(title):
  oc = ObjectContainer(title2 = title)
  oc.add(DirectoryObject(key = Callback(ShowListSort, title = "Shows Expiring Soon", sort='video.expires_at&order=asc'), title = "Shows Expiring Soon"))
  oc.add(DirectoryObject(key = Callback(MovieSections, title = "Movies Expiring Soon", sort='video.expires_at&order=asc'), title = "Movies Expiring Soon"))
  return oc
####################################################################################################
def MostPopular(title):
  oc = ObjectContainer(title2 = title)
  oc.add(DirectoryObject(key = Callback(MostPopularShows, title = "Popular Shows"), title = "Popular Shows"))
  oc.add(DirectoryObject(key = Callback(MostPopularMovies, title = "Popular Movies"), title = "Popular Movies"))
  oc.add(DirectoryObject(key = Callback(MostPopularVideos, title = "Popular Videos"), title = "Popular Videos"))
  return oc
####################################################################################################
def MostPopularShows(title):
  oc = ObjectContainer(title2 = title)
  oc.add(DirectoryObject(key = Callback(ShowListSort, title = "Popular Shows Today", sort='popular_today'), title = "Popular Shows Today"))
  oc.add(DirectoryObject(key = Callback(ShowListSort, title = "Popular Shows This Week", sort='popular_this_week'), title = "Popular Shows This Week"))
  oc.add(DirectoryObject(key = Callback(ShowListSort, title = "Popular Shows This Month", sort='popular_this_month'), title = "Popular Shows This Month"))
  oc.add(DirectoryObject(key = Callback(ShowListSort, title = "Popular Shows of All Time", sort='poplular_all_time'), title = "Popular Shows of All Time"))
  return oc
####################################################################################################
def MostPopularMovies(title):
  oc = ObjectContainer(title2 = title)
  oc.add(DirectoryObject(key = Callback(MovieSections, title = "Popular Movies Today", sort='popular_today'), title = "Popular Movies Today"))
  oc.add(DirectoryObject(key = Callback(MovieSections, title = "Popular Movies This Week", sort='popular_this_week'), title = "Popular Movies This Week"))
  oc.add(DirectoryObject(key = Callback(MovieSections, title = "Popular Movies This Month", sort='popular_this_month'), title = "Popular Movies This Month"))
  oc.add(DirectoryObject(key = Callback(MovieSections, title = "Popular Movies of All Time", sort='poplular_all_time'), title = "Popular Movies of All Time"))
  return oc
####################################################################################################
def MostPopularVideos(title):
  oc = ObjectContainer(title2 = title)
  oc.add(DirectoryObject(key = Callback(Feeds, title = "Popular Videos Today", feed_url = "http://www.hulu.com/feed/popular/videos/today"), title = "Popular Videos Today"))
  oc.add(DirectoryObject(key = Callback(Feeds, title = "Popular Videos This Week", feed_url = "http://www.hulu.com/feed/popular/videos/this_week"), title = "Popular Videos This Week"))
  oc.add(DirectoryObject(key = Callback(Feeds, title = "Popular Videos This Month", feed_url = "http://www.hulu.com/feed/popular/videos/this_month"), title = "Popular Videos This Month"))
  oc.add(DirectoryObject(key = Callback(Feeds, title = "Popular Videos of All Time", feed_url = "http://www.hulu.com/feed/popular/videos/all_time"), title = "Popular Videos of All Time"))
  return oc

####################################################################################################
def MostRecent(title):
# the recent use the show json with a &sort=release_with_popularity
  oc = ObjectContainer(title2 = title)
  oc.add(DirectoryObject(key = Callback(ShowListSort, title = "Recently Added Shows", sort='recently_added'), title = "Recently Added Shows"))
  oc.add(DirectoryObject(key = Callback(MovieSections, title = "Recently Added Movies", sort='recently_added'), title = "Recently Added Movies"))
  oc.add(DirectoryObject(key = Callback(Feeds, title = "Recently Added Videos", feed_url = "http://www.hulu.com/feed/recent/videos"), title = "Recently Added Videos"))
  return oc

####################################################################################################
def Feeds(title, feed_url):
  oc = ObjectContainer(title2 = title)

  feed = XML.ElementFromURL(feed_url)
  for item in feed.xpath('//channel/item'):
    url = item.xpath('.//guid/text()')[0]
    thumb = item.xpath('.//media:thumbnail', namespaces = NAMESPACES)[0].get('url').split('?')[0] + '?size=512x288'
    date = Datetime.ParseDate(item.xpath('.//pubDate/text()')[0])

    summary_text = item.xpath('.//description/text()')[0]
    summary_node = HTML.ElementFromString(summary_text)
    summary = summary_node.xpath('.//p/text()')[0]
 
    rating = None
    try: rating = float(REGEX_RATING_FEED.findall(summary_text)[0]) * 2
    except: pass

    title = item.xpath('.//title/text()')[0].replace("\n", " ")
    try:

      # A feed will normally contain individual episodes. Their titles are of formats similar to the following:
      #    The Voice - s2 | e15 - Quarterfinals: Live Eliminations
      # If we detect this, then we can extract the available information. If this fails, then we will simply 
      # fallback to a normal VideoClipObject
      details = REGEX_TV_EPISODE_FEED.match(title).groupdict()

      oc.add(EpisodeObject(
        url = url,
        title = details['title'],
        summary = summary,
        show = details['show'],
        season = int(details['season']),
        index = int(details['episode']),
        thumb = thumb,
        originally_available_at = date,
        rating = rating))
    except:

      oc.add(VideoClipObject(
        url = url,
        title = title,
        summary = summary,
        thumb = thumb,
        originally_available_at = date,
        rating = rating))

  return oc

####################################################################################################
def ListShows(title, channel, item_type, display, page = 0):
  oc = ObjectContainer()

  channel = channel.replace(' ','%20')
  shows_page = HTTP.Request(URL_LISTINGS % (channel, display, item_type, str(page))).content
  html_content = REGEX_SHOW_LISTINGS.search(shows_page).group('content').decode('unicode_escape')
  html_page = HTML.ElementFromString(html_content)

  for item in html_page.xpath('//a[@class = "info_hover"]'):
    original_url = item.get('href').split('?')[0]
    if original_url.startswith('http://www.hulu.com/') == False:
      continue

    # There are a very, very small percentage of videos for which they appear to contain 'invalid'
    # JSON. At present, there is no known workaround, so we should simply skip it.
    info_url = original_url.replace('http://www.hulu.com/', 'http://www.hulu.com/shows/info/')
    Log('the values of info_url is %s' %info_url)
    try: details = JSON.ObjectFromURL(info_url, headers = {'X-Requested-With': 'XMLHttpRequest'})
    except: continue

    tags = []
    if 'taggings' in details:
      tags = [ tag['tag_name'] for tag in details['taggings'] ]
    if details.has_key('films_count'):
      oc.add(MovieObject(
        url = HuluVidURL + str(details[id]),
        title = details['name'],
        summary = details['description'],
        thumb = details['thumbnail_url'],
        tags = tags,
        originally_available_at = Datetime.ParseDate(details['film_date'])))

    elif details.has_key('episodes_count') and details['episodes_count'] > 0:

      oc.add(TVShowObject(
        key = Callback(ListSeasons, title = details['name'], show_url = original_url, info_url = info_url, show_id = details['id']),
        rating_key = original_url,
        title = details['name'],
        summary = details['description'],
        thumb = details['thumbnail_url'],
        episode_count = details['episodes_count'],
        viewed_episode_count = 0,
        tags = tags))

  # Add an option for the next page. We will only return the MessageContainer if we have at least grabbed one page. If the above
  # code is faulty and the first page fails, we want to return the empty ObjectContainer. This will allow us to detect the error
  # by the tester and hopefully fix the issue quickly.
  if len(oc) > 0:
    oc.add(DirectoryObject(
      key = Callback(ListShows, title = title, channel = channel, item_type = item_type, display = display, page = page + 1),
      title = "Next..."))
  elif page > 0:
    return MessageContainer("No More Results", "There are no more shows...")


  return oc

####################################################################################################
def ListSeasons(title, show_url, info_url, show_id):
  oc = ObjectContainer(title2 = title)

  details = JSON.ObjectFromURL(info_url, headers = {'X-Requested-With': 'XMLHttpRequest'})

  if int(details['seasons_count']) > 1:
    for i in range(int(details['seasons_count'])):

      season_num = str(i+1)
      oc.add(SeasonObject(
        key = Callback(ListVideos, title = details['name'], show_id = details['id'], season = int(season_num), section='episode', show_url = show_url),
        rating_key = show_url,
        show = details['name'],
        index = int(season_num),
        title = "Season %s" % season_num,
        summary = details['description'],
        thumb = details['thumbnail_url'].split('?')[0] + '?size=512x288'
      ))

  else:
    try:
      show_id = details['id']
      show_name = details['name']
      season = '1'

      return ListVideos(title, show_id, season, section='episode', show_url = show_url)
    except: 
      pass

  return oc
 
###################################################################################################
# This will produce any videos from shows that are on Hulu. 
# The input required is with show_id (included function HuluID if need to pull from a url), section (episode or clip), 
# sort (release_with_popularity or seasons_and_release but others are available see sort comments at top), 
# position (set at start of function acts like page number), and access_token (pulled from HuluToken function below)
@route(PREFIX + '/listvideos', season=int)
def ListVideos(title, show_id, season, section, show_url, position = 0):
  oc = ObjectContainer(title2 = title)
  # they change the access_token for the JSON, so now just pulling it from page
  access_token = HuluToken(show_url)
  # this works with show_id, section, show_id, sort, section, position, access_token. And add &season_number= to end
  if section == 'clip':
    sort = 'release_with_popularity'
  else:
    sort = 'seasons_and_release'
  json_url = HuluVidJSON % (str(show_id), section, str(show_id), sort, section, str(position), access_token)
  if section == 'episode':
    json_url = json_url + '&season_number=' + str(season)
  # This below works with show_id, season, show_id, position, access_token
  # json_url = HuluEpJSON % (show_id,  str(season), show_id, str(position), str(access_token))

  try:
    data = JSON.ObjectFromURL(json_url)
  except:
    return ObjectContainer(header=L('Error'), message=L('Unable to access video data for shows'))

  for video in data['data']:
    vid_url = video['video']['id']
    vid_url = HuluVidURL + str(vid_url)
    title = video['video']['title']
    thumb = video['video']['thumbnail_url']
    duration = video['video']['duration']
    duration = float(duration) * 1000
    date = Datetime.ParseDate(video['video']['available_at'])
    summary = video['video']['description']
    if section == 'episode':
      episode =  video['video']['episode_number']
	
      oc.add(EpisodeObject(
        url = vid_url, 
        title = title,
        season = season,
        thumb = Resource.ContentsOfURLWithFallback(thumb),
        summary = summary,
        index = int(episode),
        duration = int(duration),
        originally_available_at = date))
    
    else:
      oc.add(VideoClipObject(
        url = vid_url, 
        title = title,
        thumb = Resource.ContentsOfURLWithFallback(thumb),
        summary = summary,
        duration = int(duration),
        originally_available_at = date))

  # Check to see if there are any futher results available.
  if data.has_key('total_count'):
    total_results = int(data['total_count'])
    items_per_page = 32
    start_index = int(data['position'])

    if (start_index + items_per_page) < total_results:
      oc.add(NextPageObject(
        key = Callback(ListVideos, title = title, url = url, section=section, position = position + 32), 
        title = L("Next Page ...")
      ))

  if len(oc) < 1:
    Log ('still no value for objects')
    return ObjectContainer(header="Empty", message="There are no videos to display for this show right now.")      
  else:
    return oc
###############################################################################################################
# This function pulls the API_DONUT from each show page for it to be entered into the JSON data url for Hulu
# Got an error because they changed the access token for the JSON, so pulling that data from the page now
# the access token is the API_DONUT in the page
@route(PREFIX + '/hulutoken')
def HuluToken(url):
  token = ''
  content = HTTP.Request(url).content
  token = RE_HULU_TOKEN.search(content).group(1)
  return token

###############################################################################################################
# This function pulls the show ID from a show page that is needed for the JSON data url
@route(PREFIX + '/huluid')
def HuluID(url):
  ID = ''
  content = HTTP.Request(url).content
  ID = RE_HULU_ID.search(content).group(1)
  return ID

####################################################################################################
def Queue(title, page = 1):
  oc = ObjectContainer(title2 = title)

  queue_page = HTML.ElementFromURL(URL_QUEUE % page)
  for item in queue_page.xpath('//div[@id = "queue"]//tr[contains(@id, "queue")]'):

    url = item.xpath('.//td[@class = "c2"]//a')[0].get('href')
    title = ''.join(item.xpath('.//td[@class = "c2"]//a//text()'))
    thumb = item.xpath('.//td[@class = "c2"]//img')[0].get('src').split('?')[0] + '?size=512x288'
    date = item.xpath('.//td[@class = "c5"]/text()')[0]
    date = Datetime.ParseDate(date)
    duration = int(TimeToMs(item.xpath('.//td[@class = "c2"]//span/text()')[0]))

    rating_full = len(item.xpath('.//td[@class = "c4"]/img[contains(@src, "full")]'))
    rating_half = len(item.xpath('.//td[@class = "c4"]/img[contains(@src, "half")]'))
    rating = float((2 * rating_full) + rating_half)

    summary = None
    try: summary = item.xpath('.//td[@class = "c2"]//div[@class = "expire-warning"]//text()')[0]
    except: pass

    video_details = item.xpath('.//td[@class = "c3"]/text()')[0]
    if video_details.find('Movie') > -1:
      oc.add(MovieObject(
        url = url,
        title = title,
        summary = summary,
        thumb = thumb,
        rating = rating,
        originally_available_at = date,
        duration = duration))

    else:
      tv_details = REGEX_TV_EPISODE_QUEUE.match(video_details)
      if tv_details != None:

        tv_details_dict = tv_details.groupdict()
        show = title.split(':')[0]
        episode_title = title.split(':')[1]
        oc.add(EpisodeObject(
          url = url,
          show = show,
          title = episode_title,
          summary = summary,
          season = int(tv_details_dict['season']),
          index = int(tv_details_dict['episode']),
          thumb = thumb,
          rating = rating,
          originally_available_at = date,
          duration = duration))

      else:
        oc.add(VideoClipObject(
          url = url,
          title = title,
          summary = summary,
          thumb = thumb,
          rating = rating,
          originally_available_at = date,
          duration = duration))

  # Check to see if the user has any more pages...
  page_control = queue_page.xpath('//div[@class = "page"]')
  if len(page_control) > 0:
    total_pages = int(page_control[0].xpath('.//li[@class = "total"]/a/text()')[0])
    if page < total_pages:
      oc.add(DirectoryObject(key = Callback(Queue, title = "My Queue", page = page + 1), title = "Next..."))

  return oc

####################################################################################################
def TimeToMs(timecode):
  seconds = 0
  timecode = timecode.strip('(').rstrip(')')

  try:
    duration = timecode.split(':')
    duration.reverse()

    for i in range(0, len(duration)):
      seconds += int(duration[i]) * (60**i)
  except:
    pass

  return seconds * 1000

####################################################################################################
def Recommended(title, url):
  oc = ObjectContainer()

  shows_page = HTTP.Request(url, headers = {'X-Requested-With': 'XMLHttpRequest'}).content
  html_content = REGEX_RECOMMENDED_LISTINGS.findall(shows_page)[0].decode('unicode_escape')
  html_page = HTML.ElementFromString(html_content)

  for item in html_page.xpath('//span/a[contains(@class, "info_hover")]'):
    original_url = item.get('href').split('?')[0]
    if original_url.startswith('http://www.hulu.com/') == False:
      continue

    info_url = original_url.replace('http://www.hulu.com/', 'http://www.hulu.com/shows/info/')
    details = JSON.ObjectFromURL(info_url, headers = {'X-Requested-With': 'XMLHttpRequest'})

    vid_id = details['id']
    tags = []
    if 'taggings' in details:
      tags = [ tag['tag_name'] for tag in details['taggings'] ]

    if details.has_key('films_count'):
      oc.add(MovieObject(
        url = HuluVidURL + str(vid_id),
        title = details['name'],
        summary = details['description'],
        thumb = details['thumbnail_url'].split('?')[0] + '?size=512x288',
        tags = tags,
        originally_available_at = Datetime.ParseDate(details['film_date'])))

    elif details.has_key('episodes_count') and details['episodes_count'] > 0:

      oc.add(TVShowObject(
        key = Callback(ListSeasons, title = details['name'], show_url = original_url, info_url = info_url, show_id = details['id']),
        rating_key = original_url,
        title = details['name'],
        summary = details['description'],
        thumb = details['thumbnail_url'].split('?')[0] + '?size=512x288',
        episode_count = details['episodes_count'],
        viewed_episode_count = 0,
        tags = tags))

  return oc

####################################################################################################
def Favorites(title):
  oc = ObjectContainer(title2 = title)

  url = 'http://www.hulu.com/favorites/favorites_nav?user_id=' + Dict['_hulu_uid']
  favourites_page = HTML.ElementFromURL(url)
  for show in favourites_page.xpath("//div[@class='fav-nav-show']"):

    original_url = show.xpath("./a")[0].get("href")

    info_url = original_url.replace('http://www.hulu.com/', 'http://www.hulu.com/shows/info/')
    details = JSON.ObjectFromURL(info_url, headers = {'X-Requested-With': 'XMLHttpRequest'})

    tags = []
    if 'taggings' in details:
      tags = [ tag['tag_name'] for tag in details['taggings'] ]

    oc.add(TVShowObject(
      key = Callback(ListSeasons, title = details['name'], show_url = original_url, info_url = info_url, show_id = details['id']),
      rating_key = original_url,
      title = details['name'],
      summary = details['description'],
      thumb = details['thumbnail_url'].split('?')[0] + '?size=512x288',
      episode_count = details['episodes_count'],
      viewed_episode_count = 0,
      tags = tags))

  return oc

#######################################################################################################
# This function allows you to create a sort of all shows by recently added, many popular sorts and possibly more
# The arguments for the JSON url used in this function are sort (see comment at 
# top of channel for a full list of pulls mainly new and popular variations), position (act like page), and 
# access_token (pulled by function and url). I did not use the more basic HuluJSON with main_type and section
# so I could pulled all shows with any video. 
# NOTE: the access token is the same on all Hulu pages, so any url can be used including the base (HuluURL)
# that I used below.
def ShowListSort(title, sort, position=0):

  oc = ObjectContainer(title2 = title)
  # they change the access_token for the JSON, often so just pulling it URL
  access_token = HuluToken(HuluURL)
  # This below works with sort, position, access_token
  json_url = HuluShowJson % (sort, int(position), access_token)

  try:
    data = JSON.ObjectFromURL(json_url)
  except:
    return ObjectContainer(header=L('Error'), message=L('Unable to access show data'))

  for show in data['data']:
    show_id = show['show']['id']
    show_url = HuluShowURL + str(show_id)
    title = show['show']['name']
    episodes =  show['show']['episodes_count']
    thumb = show['show']['thumbnail_url']
    clips =  show['show']['clips_count']
    summary = show['show']['description']
    seasons =  show['show']['seasons_count']

    if seasons:	
      oc.add(DirectoryObject(key = Callback(ShowSeasons, title=title, seasons=seasons, show_url=show_url, show_id=show_id, thumb=thumb),
        title = title,
        thumb = Resource.ContentsOfURLWithFallback(thumb),
        summary = summary))
    else:
	# These are video clips that go directly to the ListVideos function to produce videos
      oc.add(DirectoryObject(key = Callback(ListVideos, title=title, show_id=show_id, season=0, section='clip', show_url=show_url),
        title = title,
        thumb = Resource.ContentsOfURLWithFallback(thumb),
        summary = summary))

  # Check to see if there are any futher results available.
  if data.has_key('total_count'):
    total_results = int(data['total_count'])
    items_per_page = 32
    start_index = int(data['position'])

    if (start_index + items_per_page) < total_results:
      oc.add(NextPageObject(
        key = Callback(ShowListSort, title = title, sort=sort, position = position + 32), 
        title = L("Next Page ...")
      ))

  if len(oc) < 1:
    Log ('still no value for objects')
    return ObjectContainer(header="Empty", message="There are no videos to display for this show right now.")      
  else:
    return oc

####################################################################################################
# This function creates season folders for the sorted shows sent from the ShowListSort function above
# Since all info was pulled in function above, it does not have to do a call on the website
def ShowSeasons(title, show_url, seasons, show_id, thumb):
  oc = ObjectContainer(title2 = title)

  if int(seasons) > 1:
    for i in range(int(seasons)):

      season_num = str(i+1)
      oc.add(SeasonObject(
        key = Callback(ListVideos, title = title, show_id = show_id, season = int(season_num), section='episode', show_url = show_url),
        rating_key = show_url,
        show = title,
        index = int(season_num),
        title = "Season %s" % season_num,
        thumb = thumb
      ))
  return oc
####################################################################################################
# This function allows you to create a sort of all movies by recently added, many popular sorts and possibly more
# The arguments for the JSON url used in this function are main_type (here it uses movie), section (films, short, or trailers), sort (see comment at 
# top of channel for a full list of pulls mainly new and popular variations), position (act like page), and 
# access_token (pulled by function and url)
# NOTE: the access token is the same on all Hulu pages, so any url can be used including the base (HuluURL)
# that I used below.
def MovieListSort(title, section, sort, position=0):

  oc = ObjectContainer(title2 = title)
  # they change the access_token often for the JSON, so just pulling it from page
  access_token = HuluToken(HuluURL)
  main_type = 'movies'
  json_url = HuluJson % (main_type, section, sort, int(position), access_token)

  try:
    data = JSON.ObjectFromURL(json_url)
  except:
    return ObjectContainer(header=L('Error'), message=L('Unable to access show data'))

  for movie in data['data']:
    id = movie['video']['id']
    movie_url = HuluVidURL + str(id)
    title = movie['video']['title']
    duration =  movie['video']['duration']
    duration = float(duration) * 1000
    thumb = movie['video']['thumbnail_url']
    date =  Datetime.ParseDate(movie['video']['available_at'])
    summary = movie['video']['description']

    oc.add(MovieObject(
      url = movie_url,
      title = title,
      summary = summary,
      thumb = thumb,
      duration = int(duration),
      originally_available_at = date))

  # Check to see if there are any futher results available.
  if data.has_key('total_count'):
    total_results = int(data['total_count'])
    items_per_page = 32
    start_index = int(data['position'])

    if (start_index + items_per_page) < total_results:
      oc.add(NextPageObject(
        key = Callback(MovieListSort, title = title, section=section, sort=sort, genre=genre, position = position + 32), 
        title = L("Next Page ...")
      ))

  if len(oc) < 1:
    Log ('still no value for objects')
    return ObjectContainer(header="Empty", message="There are no videos to display for this show right now.")      
  else:
    return oc

####################################################################################################
# This function separates sort pulls for movies into three sections, shorts, trailers, and films
def MovieSections(title, sort):
  oc = ObjectContainer(title2 = title)

  oc = ObjectContainer(title2 = title)
  oc.add(DirectoryObject(key = Callback(MovieListSort, title = "Shorts", section='shorts', sort=sort), title = "Shorts"))
  oc.add(DirectoryObject(key = Callback(MovieListSort, title = "Trailers", section='trailers', sort=sort), title = "Trailers"))
  oc.add(DirectoryObject(key = Callback(MovieListSort, title = "Films", section='films', sort=sort), title = "Films"))
  return oc
