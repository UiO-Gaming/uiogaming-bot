from discord.ext import commands
import discord

from requests import post
from re import compile, sub

from cogs.utils import embed_templates


async def set_color(color: str) -> int:
    """
    Converts anilist colors to hext

    Parameters
    ----------
    color: The color string returned from the Anilist API

    Returns
    ----------
    (int): The color in hex for use in discord embeds
    """

    colors = {
        'blue': 0x3db4f2,
        'purple': 0xc063ff,
        'pink': 0xFC9DD6,
        'orange': 0xEF881A,
        'red': 0xE13333,
        'green': 0x4CCA51,
        'gray': 0x677B94
    }
    if color in colors:
        color = colors[color]
    else:
        color = color.replace('#', '0x')
        color = int(color, 0)
    return color


async def convert_media_format(media_format: str):
    """
    Translates media format names into norwegian

    Parameters
    ----------
    media_format: The english media format name returned from the Anilist API

    Returns
    ----------
    (str): The media format name in norwegian. If a translation doesn't exist it returns the english name
    """

    media_formats = {
        'TV': 'TV-Serie',
        'TV_SHORT': 'Kort TV-Serie',
        'MOVIE': 'Film',
        'SPECIAL': 'Ekstramateriale',
        'MUSIC': 'Musikk',
        'MANGA': 'Manga',
        'NOVEL': 'Novelle',
        'ONE_SHOT': 'Kort Manga'
    }
    try:
        return media_formats[media_format]
    except KeyError:
        return media_format


async def convert_language_names(language_name: str):
    """
    Translates language names into norwegian

    Parameters
    ----------
    language_name: The english language name returned from the Anilist API

    Returns
    ----------
    (str): The language name in norwegian. If a translation doesn't exist it returns the english name
    """

    languages = {
        'JAPANESE': 'Japansk',
        'ENGLISH': 'Engelsk',
        'KOREAN': 'Koreansk',
        'ITALIAN': 'Italiensk',
        'SPANISH': 'Spansk',
        'PORTUGUESE': 'Portugisisk',
        'FRENCH': 'Fransk',
        'GERMAN': 'Tysk',
        'HEBREW': 'Hebraisk',
        'HUNGARIAN': 'Ungarsk'
    }
    try:
        return languages[language_name]
    except KeyError:
        return language_name


async def convert_role_names(role_name: str):
    """
    Translates role names into norwegian

    Parameters
    ----------
    role_name: The english role name returned from the Anilist API

    Returns
    ----------
    (str): The role name in norwegian. If a translation doesn't exist it returns the english name
    """

    roles = {
        'MAIN': 'Hovedkarakter',
        'SUPPORTING': 'Bikarakter/Biperson',
        'BACKGROUND': 'Statist'
    }
    try:
        return roles[role_name]
    except KeyError:
        return role_name


async def convert_status(status: str):
    """
    Translates role names into norwegian

    Parameters
    ----------
    status: The english status name returned from the Anilist API

    Returns
    ----------
    (str): The status name in norwegian. If a translation doesn't exist it returns the english name
    """

    statuses = {
        'FINISHED': 'Fullt utgitt',
        'RELEASING': 'Pågående',
        'NOT_YET_RELEASED': 'Ikke utgitt enda',
        'CANCELLED': 'Kansellert'
    }
    try:
        return statuses[status]
    except KeyError:
        return status


async def remove_html(text):
    """
    Removes HTML tag elements

    Parameters
    ----------
    text: The raw HTML

    Returns
    ----------
    (str): The input string without HTML tags
    """

    compiled = compile(r'<.*?>')
    clean_text = sub(compiled, '', text)
    return clean_text


class Anime(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.bot_has_permissions(embed_links=True)
    @commands.cooldown(1, 5, commands.BucketType.guild)
    @commands.group()
    async def anilist(self, ctx):
        """
        Se informasjon om noe fra Anilist
        """

        if ctx.invoked_subcommand is None:
            await ctx.send_help(ctx.command)

    @anilist.command(aliases=['profile'])
    async def profil(self, ctx, *, bruker: str):
        """
        Viser informasjon om en Anilist-profil
        """

        async with ctx.channel.typing():

            #  GraphQL
            query = """
            query ($name: String) {
                User (name: $name) {
                    name
                    siteUrl
                    avatar {
                        large
                    }
                    options {
                        profileColor
                    }
                    statistics {
                        anime {
                            minutesWatched
                            statuses {
                                count
                                status
                            }
                        }
                        manga {
                            chaptersRead
                            statuses {
                                count
                                status
                            }
                        }
                    }
                    favourites {
                        anime (perPage: 3) {
                            nodes {
                                isAdult
                                title {
                                    romaji
                                }
                                siteUrl
                            }
                        }
                        manga (perPage: 3) {
                                nodes {
                                isAdult
                                title {
                                    romaji
                                }
                                siteUrl
                            }
                        }
                        studios (perPage: 3) {
                            nodes {
                                name
                                siteUrl
                            }
                        }
                        characters (perPage: 3) {
                            nodes {
                                name {
                                    full
                                }
                                siteUrl
                            }
                        }
                        staff (perPage: 3) {
                            nodes {
                                name {
                                    full
                                }
                                siteUrl
                            }
                        }
                    }
                }
            }
            """
            variables = {
                'name': bruker
            }
            try:
                data = post(
                    'https://graphql.anilist.co',
                    json={'query': query, 'variables': variables}).json()
                data = data['data']['User']
                url = data['siteUrl']
            except TypeError:
                embed = embed_templates.error_fatal(ctx, text='Kunne ikke finne brukeren!')
                return await ctx.send(embed=embed)

            user_name = data['name']
            profile_pic = data['avatar']['large']
            days_watched = round(data['statistics']['anime']['minutesWatched'] / 1440, 1)
            chapters_read = data['statistics']['manga']['chaptersRead']
            color = await set_color(data['options']['profileColor'])

            anime_statuses = {}
            for status in data['statistics']['anime']['statuses']:
                status_name = status['status']
                status_count = status['count']
                anime_statuses.update({f'{status_name}': {'count': status_count}})

            manga_statuses = {}
            for status in data['statistics']['manga']['statuses']:
                status_name = status['status']
                status_count = status['count']
                manga_statuses.update({f'{status_name}': {'count': status_count}})

            try:
                anime_completed = anime_statuses['COMPLETED']['count']
            except KeyError:
                anime_completed = 0
            try:
                manga_completed = manga_statuses['COMPLETED']['count']
            except KeyError:
                manga_completed = 0

            favourite_anime = []
            for anime in data['favourites']['anime']['nodes']:
                try:
                    if anime['isAdult'] is True:
                        nsfwtag = ' (NSFW)'
                    else:
                        nsfwtag = ''
                    anime_name = anime['title']['romaji']
                    anime_url = anime['siteUrl']
                    favourite_anime.append(f'[{anime_name}]({anime_url}){nsfwtag}')
                except KeyError:
                    pass
            favourite_anime = ' | '.join(favourite_anime)

            favourite_manga = []
            for manga in data['favourites']['manga']['nodes']:
                try:
                    if manga['isAdult'] is True:
                        nsfwtag = ' (NSFW)'
                    else:
                        nsfwtag = ''
                    manga_name = manga['title']['romaji']
                    manga_url = manga['siteUrl']
                    favourite_manga.append(f'[{manga_name}]({manga_url}){nsfwtag}')
                except KeyError:
                    pass
            favourite_manga = ' | '.join(favourite_manga)

            favourite_character = []
            for character in data['favourites']['characters']['nodes']:
                try:
                    character_name = character['name']['full']
                    character_url = character['siteUrl']
                    favourite_character.append(f'[{character_name}]({character_url})')
                except KeyError:
                    pass
            favourite_character = ' | '.join(favourite_character)

            favourite_staff = []
            for staff in data['favourites']['staff']['nodes']:
                try:
                    staff_name = staff['name']['full']
                    staff_url = staff['siteUrl']
                    favourite_staff.append(f'[{staff_name}]({staff_url})')
                except KeyError:
                    pass
            favourite_staff = ' | '.join(favourite_staff)

            favourite_studio = []
            for studio in data['favourites']['studios']['nodes']:
                try:
                    studio_name = studio['name']
                    studio_url = studio['siteUrl']
                    favourite_studio.append(f'[{studio_name}]({studio_url})')
                except KeyError:
                    pass
            favourite_studio = ' | '.join(favourite_studio)

            embed = discord.Embed(title=user_name, color=color, url=url)
            embed.set_author(name='Anilist', icon_url='https://anilist.co/img/logo_al.png')
            embed.set_thumbnail(url=profile_pic)
            embed.add_field(name='Antall dager sett', value=days_watched)
            embed.add_field(name='Antall anime sett', value=anime_completed)
            embed.add_field(name='Antall kapitler lest', value=chapters_read)
            embed.add_field(name='Antall manga lest', value=manga_completed)
            if favourite_anime != '':
                embed.add_field(name='Noen favorittanime', value=favourite_anime, inline=False)
            if favourite_manga != '':
                embed.add_field(name='Noen favorittmanga', value=favourite_manga, inline=False)
            if favourite_character != '':
                embed.add_field(name='Noen favorittkarakterer', value=favourite_character, inline=False)
            if favourite_studio != '':
                embed.add_field(name='Noen favorittstudioer', value=favourite_studio, inline=False)
            if favourite_studio != '':
                embed.add_field(name='Noen favorittskapere', value=favourite_staff, inline=False)
            embed = embed_templates.default_footer(ctx, embed)
            await ctx.send(embed=embed)


    @anilist.command(aliases=['anime'])
    async def animestats(self, ctx, *, bruker: str):
        """
        Viser animeinformasjon til en Anilist-profil
        """

        async with ctx.channel.typing():

            #  GraphQL
            query = """
            query ($name: String) {
                User (name: $name) {
                    name
                    siteUrl
                    avatar {
                        large
                    }
                    options {
                        profileColor
                    }
                    statistics {
                        anime {
                            minutesWatched
                            episodesWatched
                            meanScore
                            statuses {
                                count
                                status
                                minutesWatched
                            }
                            studios (limit: 3, sort: COUNT_DESC) {
                                studio {
                                    name
                                    siteUrl
                                }
                            }
                            genres (limit: 3, sort: COUNT_DESC) {
                                genre
                            }
                        }
                    }
                }
            }
            """
            variables = {
                'name': bruker
            }
            try:
                data = post(
                    'https://graphql.anilist.co',
                    json={'query': query, 'variables': variables}).json()
                data = data['data']['User']
                url = data['siteUrl']
            except TypeError:
                embed = embed_templates.error_fatal(ctx, text='Kunne ikke finne brukeren!')
                return await ctx.send(embed=embed)

            user_name = data['name']
            profile_pic = data['avatar']['large']
            days_watched = round(data['statistics']['anime']['minutesWatched'] / 1440, 1)
            episodes_watched = data['statistics']['anime']['episodesWatched']
            color = await set_color(data['options']['profileColor'])

            statuses = {}
            for status in data['statistics']['anime']['statuses']:
                status_name = status['status']
                status_count = status['count']
                status_minutes = status['minutesWatched']
                statuses.update({f'{status_name}': {'count': status_count, 'minutes': status_minutes}})

            try:
                completed = statuses['COMPLETED']['count']
            except KeyError:
                completed = 0
            try:
                watching = statuses['CURRENT']['count']
            except KeyError:
                watching = 0
            try:
                planning = statuses['PLANNING']['count']
                planning_days = round(statuses['PLANNING']['minutes'] / 1440, 1)
            except KeyError:
                planning = 0
                planning_days = 0
            try:
                dropped = statuses['DROPPED']['count']
            except KeyError:
                dropped = 0

            anime_mean_score = data['statistics']['anime']['meanScore']
            if anime_mean_score == 0:
                anime_mean_score = '**Ingen**'

            genres = []
            for genre in data['statistics']['anime']['genres']:
                genres.append(genre['genre'])
            most_watched_genres = ', '.join(genres)

            studios = []
            for studio in data['statistics']['anime']['studios']:
                studio_name = studio['studio']['name']
                studio_url = studio['studio']['siteUrl']
                studios.append(f'[{studio_name}]({studio_url})')
            most_watched_studios = ' | '.join(studios)

            embed = discord.Embed(title=user_name, color=color, url=url)
            embed.set_author(name='Anilist', icon_url='https://anilist.co/img/logo_al.png')
            embed.set_thumbnail(url=profile_pic)
            embed.add_field(name='Gj.snittsvurdering gitt', value=anime_mean_score)
            embed.add_field(name='Antall dager sett', value=days_watched)
            embed.add_field(name='Antall episoder sett', value=episodes_watched)
            embed.add_field(name='Antall anime sett', value=completed)
            embed.add_field(name='Ser på nå', value=watching)
            embed.add_field(name='Planlegger å se', value=f'{planning}\n({planning_days} dager)')
            embed.add_field(name='Droppet', value=dropped)
            if most_watched_genres != '':
                embed.add_field(name='Mest sette sjangere', value=most_watched_genres, inline=False)
            if most_watched_studios != '':
                embed.add_field(name='Mest sette studioer', value=most_watched_studios, inline=False)
            embed = embed_templates.default_footer(ctx, embed)
            await ctx.send(embed=embed)

    @anilist.command(aliases=['manga'])
    async def mangastats(self, ctx, *, bruker: str):
        """
        Viser mnagainformasjonen til en Anilist-profil
        """

        async with ctx.channel.typing():

            #  GraphQL
            query = """
            query ($name: String) {
                User(name: $name) {
                    name
                    siteUrl
                    avatar {
                        large
                    }
                    options {
                        profileColor
                    }
                    statistics {
                        manga {
                            chaptersRead
                            volumesRead
                            meanScore
                            statuses {
                                count
                                status
                                chaptersRead
                            }
                            staff (limit: 3, sort: COUNT_DESC) {
                                staff {
                                    name {
                                        full
                                    }
                                    siteUrl
                                }
                            }
                            genres (limit: 3, sort: COUNT_DESC) {
                                genre
                            }
                        }
                    }
                }
            }
            """
            variables = {
                'name': bruker
            }

            try:
                data = post(
                    'https://graphql.anilist.co',
                    json={'query': query, 'variables': variables}).json()
                data = data['data']['User']
                url = data['siteUrl']
            except TypeError:
                embed = embed_templates.error_fatal(ctx, text='Kunne ikke finne brukeren!')
                return await ctx.send(embed=embed)

            user_name = data['name']
            profile_pic = data['avatar']['large']
            chapters_read = round(data['statistics']['manga']['chaptersRead'] / 1440, 1)
            volumes_read = data['statistics']['manga']['volumesRead']
            color = await set_color(data['options']['profileColor'])

            statuses = {}
            for status in data['statistics']['manga']['statuses']:
                status_name = status['status']
                status_count = status['count']
                status_minutes = status['chaptersRead']
                statuses.update({f'{status_name}': {'count': status_count, 'minutes': status_minutes}})

            try:
                completed = statuses['COMPLETED']['count']
            except KeyError:
                completed = 0
            try:
                reading = statuses['CURRENT']['count']
            except KeyError:
                reading = 0
            try:
                planning = statuses['PLANNING']['count']
                planning_days = statuses['PLANNING']['chaptersRead']
            except KeyError:
                planning = 0
                planning_days = 0
            try:
                dropped = statuses['DROPPED']['count']
            except KeyError:
                dropped = 0

            manga_mean_score = data['statistics']['manga']['meanScore']
            if manga_mean_score == 0:
                manga_mean_score = '**Ingen**'

            genres = []
            for genre in data['statistics']['manga']['genres']:
                genres.append(genre['genre'])
            most_read_genres = ', '.join(genres)

            staff = []
            for staffmember in data['statistics']['manga']['staff']:
                staff_name = staffmember['staff']['name']['full']
                staff_url = staffmember['staff']['siteUrl']
                staff.append(f'[{staff_name}]({staff_url})')
            most_read_staff = ' | '.join(staff)

            embed = discord.Embed(title=user_name, color=color, url=url)
            embed.set_author(name='Anilist', icon_url='https://anilist.co/img/logo_al.png')
            embed.set_thumbnail(url=profile_pic)
            embed.add_field(name='Gj.snittsvurdering gitt', value=manga_mean_score)
            embed.add_field(name='Antall kapitler lest', value=chapters_read)
            embed.add_field(name='Antall volum lest', value=volumes_read)
            embed.add_field(name='Antall manga lest', value=completed)
            embed.add_field(name='Leser nå', value=reading)
            embed.add_field(name='Planlegger å lese', value=f'{planning}\n({planning_days} kapitler)')
            embed.add_field(name='Droppet', value=dropped)
            if most_read_genres != '':
                embed.add_field(name='Mest leste sjangere', value=most_read_genres, inline=False)
            if most_read_staff != '':
                embed.add_field(name='Mest leste skapere', value=most_read_staff, inline=False)
            embed = embed_templates.default_footer(ctx, embed)
            await ctx.send(embed=embed)

    @commands.bot_has_permissions(embed_links=True)
    @commands.cooldown(1, 5, commands.BucketType.guild)
    @commands.command()
    async def anime(self, ctx, *, animenavn: str):
        """
        Viser informasjon om en anime
        """

        async with ctx.channel.typing():

            #  GraphQL
            query = '''
            query ($search: String, $isMain: Boolean) {
                Media (search: $search, type: ANIME) {
                    siteUrl
                    format
                    status
                    description (asHtml: false)
                    episodes
                    duration
                    genres
                    isAdult
                    bannerImage
                    meanScore
                    coverImage {
                        large
                        color
                    }
                    startDate {
                        year
                        month
                        day
                    }
                    endDate {
                        year
                        month
                        day
                    }
                    title {
                        romaji
                        english
                        native
                    }
                    studios (isMain: $isMain) {
                        nodes {
                            name
                            siteUrl
                        }
                    }
                    staff (sort: ROLE) {
                        edges {
                            role
                            node {
                                siteUrl
                                name {
                                    first
                                    last
                                    native
                                }
                            }
                        }
                    }
                }
            }
            '''
            variables = {
                'search': animenavn,
                'isMain': True
            }
            try:
                data = post('https://graphql.anilist.co', json={'query': query, 'variables': variables}).json()
                data = data['data']['Media']
                url = data['siteUrl']
            except TypeError:
                embed = embed_templates.error_fatal('Kunne ikke finne animen!')
                return await ctx.send(embed=embed)

            nsfw = data['isAdult']
            if nsfw:
                embed = embed_templates.error_fatal(ctx, text='Animen du søkte på er NSFW. ' +
                                                              'Gjør kommandoen i en NSFW-kanal i stedet')
                return await ctx.send(embed=embed)

            cover_image = data['coverImage']['large']
            banner_image = data['bannerImage']
            mean_score = data['meanScore']

            color = data['coverImage']['color']
            if not color:
                color = 0x02A9FF
            else:
                color = color.replace('#', '0x')
                color = int(color, 0)

            title_romaji = data['title']['romaji']
            title_native = data['title']['native']
            title_english = data['title']['english']
            titles = [title_romaji, title_native, title_english]
            for i, title in enumerate(titles):
                if title is None:
                    titles[i] = ''
            title_romaji, title_native, title_english = titles

            description = data['description']
            if description:
                description = await remove_html(data['description'])
            else:
                description = ''
            genres = ', '.join(data['genres'])

            studios = data['studios']['nodes']
            studios_string = ''
            for studio in studios:
                studio_name = studio['name']
                studio_url = studio['siteUrl']
                studios_string += f'[{studio_name}]({studio_url})\n'

            staff = data['staff']['edges']
            director_string = ''
            for staff_member in staff:
                if staff_member['role'] == 'Director':
                    director_first_name = staff_member['node']['name']['first']
                    director_last_name = staff_member['node']['name']['last']
                    director_native_name = staff_member['node']['name']['native']
                    director_url = staff_member['node']['siteUrl']
                    director_string += f'[{director_first_name} {director_last_name} ' +\
                                       f'({director_native_name})]({director_url})'

            episodes = data['episodes']
            duration = data['duration']

            release_day = data['startDate']['day']
            release_month = data['startDate']['month']
            release_year = data['startDate']['year']
            end_day = data['endDate']['day']
            end_month = data['endDate']['month']
            end_year = data['endDate']['year']

            numbers = [episodes, duration, release_day, release_month, release_year, end_day, end_month, end_year]
            for i, number in enumerate(numbers):
                if number is None:
                    numbers[i] = '?'
            episodes, duration, release_day, release_month, release_year, end_day, end_month, end_year = numbers
            length_string = ''
            if duration == 1:
                length_string += 'minutt '
            else:
                length_string += 'minutter '
            if episodes == 1:
                length_string += 'lang'
            else:
                length_string += 'lange'

            release_date = f'{release_day}.{release_month}.{release_year}'
            end_date = f'{end_day}.{end_month}.{end_year}'
            if release_date == end_date:
                date = release_date
            else:
                date = f'{release_date} - {end_date}'

            status = data['status']
            status = await convert_status(status)

            media_format = data['format']
            media_format = await convert_media_format(media_format)

            embed = discord.Embed(color=color, title=title_romaji, url=url,
                                  description=f'{title_native}\n{title_english}')
            embed.set_thumbnail(url=cover_image)
            embed.add_field(name='Format', value=media_format)
            embed.add_field(name='Status', value=status)
            if studios_string:
                embed.add_field(name='Studio', value=studios_string)
            if director_string:
                embed.add_field(name='Regissør', value=director_string)
            embed.add_field(name='Utgivelsesdato', value=date)
            if media_format == 'Film':
                embed.add_field(name='Lengde', value=f'{duration} minutter')
            else:
                embed.add_field(name='Episoder', value=f'{episodes} ({duration} {length_string})')
            if mean_score:
                embed.add_field(name='Gj.snittsvurdering', value=f'{mean_score}/100')
            embed.add_field(name='Sjangere', value=genres)
            if len(description) < 1024 and description != '':
                embed.add_field(name='Sammendrag', value=description, inline=False)
            if banner_image:
                embed.set_image(url=banner_image)
            embed = embed_templates.default_footer(ctx, embed)
            await ctx.send(embed=embed)

    @commands.bot_has_permissions(embed_links=True)
    @commands.cooldown(1, 5, commands.BucketType.guild)
    @commands.command()
    async def manga(self, ctx, *, manganavn: str):
        """
        Viser informasjon om en manga
        """

        async with ctx.channel.typing():

            query = '''
                query ($search: String) {
                    Media (search: $search, type: MANGA) {
                        siteUrl
                        format
                        status
                        description (asHtml: false)
                        volumes
                        chapters
                        genres
                        isAdult
                        bannerImage
                        meanScore
                        coverImage {
                            large
                            color
                        }
                        startDate {
                            year
                            month
                            day
                        }
                        endDate {
                            year
                            month
                            day
                        }
                        title {
                            romaji
                            english
                            native
                        }
                        staff(sort: ROLE) {
                            edges {
                                role
                                node {
                                    siteUrl
                                    name {
                                        first
                                        last
                                        native
                                    }
                                }
                            }
                        }
                    }
                }
                '''
            variables = {
                'search': manganavn
            }
            try:
                data = post('https://graphql.anilist.co', json={'query': query, 'variables': variables}).json()
                data = data['data']['Media']
                url = data['siteUrl']
            except TypeError:
                embed = embed_templates.error_fatal('Kunne ikke finne Mangaen!')
                return await ctx.send(embed=embed)

            nsfw = data['isAdult']
            if nsfw:
                embed = embed_templates.error_fatal(ctx, text='Mangaen du søkte på er NSFW. ' +
                                                              'Gjør kommandoen i en NSFW-kanal i stedet')
                return await ctx.send(embed=embed)

            cover_image = data['coverImage']['large']
            banner_image = data['bannerImage']
            mean_score = data['meanScore']

            color = data['coverImage']['color']
            if not color:
                color = 0x02A9FF
            else:
                color = color.replace('#', '0x')
                color = int(color, 0)

            title_romaji = data['title']['romaji']
            title_native = data['title']['native']
            title_english = data['title']['english']
            titles = [title_romaji, title_native, title_english]
            for i, title in enumerate(titles):
                if title is None:
                    titles[i] = ''
            title_romaji, title_native, title_english = titles

            description = data['description']
            if description:
                description = await remove_html(data['description'])
            else:
                description = ''
            genres = ', '.join(data['genres'])

            staff = data['staff']['edges']
            staff_string = ''
            for staff_member in staff:
                staff_first_name = staff_member['node']['name']['first']
                staff_last_name = staff_member['node']['name']['last']
                staff_native_name = staff_member['node']['name']['native']
                staff_url = staff_member['node']['siteUrl']
                staff_string += f'[{staff_first_name} {staff_last_name} ({staff_native_name})]({staff_url})\n'

            chapters = data['chapters']
            volumes = data['volumes']

            release_day = data['startDate']['day']
            release_month = data['startDate']['month']
            release_year = data['startDate']['year']

            numbers = [chapters, volumes, release_day, release_month, release_year]
            for i, number in enumerate(numbers):
                if number is None:
                    numbers[i] = '?'
            chapters, volumes, release_day, release_month, release_year = numbers
            release_date = f'{release_day}.{release_month}.{release_year}'

            chapters_string = ''
            if chapters == 1:
                chapters_string += 'kapittel'
            else:
                chapters_string += 'kapitler'

            status = data['status']
            status = await convert_status(status)

            media_format = data['format']
            media_format = await convert_media_format(media_format)

            embed = discord.Embed(color=color, title=title_romaji, url=url,
                                  description=f'{title_native}\n{title_english}')
            embed.set_thumbnail(url=cover_image)
            embed.add_field(name='Format', value=media_format)
            embed.add_field(name='Status', value=status)
            if staff_string:
                embed.add_field(name='Laget av', value=staff_string)
            embed.add_field(name='Utgivelsesdato', value=release_date)
            embed.add_field(name='Lengde', value=f'{chapters} {chapters_string}\n{volumes} volum')
            if mean_score:
                embed.add_field(name='Gj.snittsvurdering', value=f'{mean_score}/100')
            embed.add_field(name='Sjangere', value=genres)
            if len(description) < 1024 and description != '':
                embed.add_field(name='Sammendrag', value=description, inline=False)
            if banner_image:
                embed.set_image(url=banner_image)
            embed = embed_templates.default_footer(ctx, embed)
            await ctx.send(embed=embed)

    @commands.bot_has_permissions(embed_links=True)
    @commands.cooldown(1, 5, commands.BucketType.guild)
    @commands.command(aliases=['character'])
    async def karakter(self, ctx, *, karakternavn: str):
        """Viser informasjon om en karakter"""

        async with ctx.channel.typing():

            query = '''
                query ($search: String) {
                    Character (search: $search) {
                        name {
                            full
                            native
                        }
                        siteUrl
                        favourites
                        image {
                            large
                        }
                        description (asHtml: false)
                        media (sort: POPULARITY_DESC, perPage: 1) {
                            edges {
                                node {
                                    siteUrl
                                    isAdult
                                    title {
                                        romaji
                                    }
                                }
                                characterRole
                                voiceActors {
                                    siteUrl
                                    language
                                    name {
                                        full
                                        native
                                    }
                                }
                            }
                        }
                    }
                }
                '''
            variables = {
                'search': karakternavn
            }
            try:
                data = post('https://graphql.anilist.co', json={'query': query, 'variables': variables}).json()
                data = data['data']['Character']
                url = data['siteUrl']
            except TypeError:
                embed = embed_templates.error_fatal('Kunne ikke finne karakteren!')
                return await ctx.send(embed=embed)

            name_romaji = data['name']['full']
            name_native = data['name']['native']
            image = data['image']['large']
            favourites = data['favourites']

            if data['description']:
                description = await remove_html(data['description'])
                if len(description) > 1024:
                    description = description[0:1020] + '...'
            else:
                description = '*Ingen biografi funnet* 😔'

            featured_in = []
            voice_actors = []
            for media in data['media']['edges']:
                if media['node']['isAdult'] is True:
                    nsfwtag = ' (NSFW)'
                else:
                    nsfwtag = ''
                media_name = media['node']['title']['romaji']
                media_url = media['node']['siteUrl']
                media_role = await convert_role_names(media['characterRole'])
                for voice_actor in media['voiceActors']:
                    voice_actor_url = voice_actor['siteUrl']
                    voice_actor_language = await convert_language_names(voice_actor['language'])
                    voice_actor_name = voice_actor['name']['full']
                    if voice_actor['name']['native'] != ' ' and voice_actor['name']['native'] is not None:
                        voice_actor_name += ' (' + voice_actor['name']['native'] + ')'
                    voice_actors.append(f'{voice_actor_language} stemme: [{voice_actor_name}]({voice_actor_url})')

                voice_actors_string = '\n'.join(voice_actors)
                featured_in.append(f'[{media_name}]({media_url}){nsfwtag} som {media_role}\n{voice_actors_string}')

            featured_in = '\n\n'.join(featured_in)

            embed = discord.Embed(color=0x02A9FF, title=name_romaji, url=url, description=name_native)
            embed.set_thumbnail(url=image)
            embed.add_field(name='Antall favoritter på Anilist', value=favourites, inline=False)
            embed.add_field(name='Biografi', value=description, inline=False)
            embed.add_field(name='Er med i bl.a.', value=featured_in, inline=False)
            embed = embed_templates.default_footer(ctx, embed)
            await ctx.send(embed=embed)

    @commands.bot_has_permissions(embed_links=True)
    @commands.cooldown(1, 5, commands.BucketType.guild)
    @commands.command(aliases=['staff'])
    async def skaper(self, ctx, *, skapernavn: str):
        """Viser informasjon om en skaper"""

        async with ctx.channel.typing():

            query = '''
                query ($search: String) {
                    Staff(search: $search) {
                        name {
                            full
                            native
                        }
                        siteUrl
                        image {
                            large
                        }
                        language
                        favourites
                        description(asHtml: false)
                        staffMedia(sort: POPULARITY_DESC, perPage: 2) {
                            edges {
                                staffRole
                                node {
                                    siteUrl
                                    isAdult
                                    title {
                                        romaji
                                    }
                                }
                            }
                        }
                        characters(sort: FAVOURITES_DESC, perPage: 2) {
                            edges {
                                node {
                                    name {
                                        full
                                        native
                                    }
                                    siteUrl
                                }
                            }
                        }
                    }
                }
                '''
            variables = {
                'search': skapernavn
            }
            try:
                data = post('https://graphql.anilist.co', json={'query': query, 'variables': variables}).json()
                data = data['data']['Staff']
                url = data['siteUrl']
            except TypeError:
                embed = embed_templates.error_fatal('Kunne ikke finne skaperen!')
                return await ctx.send(embed=embed)

            name_romaji = data['name']['full']
            name_native = data['name']['native']
            image = data['image']['large']
            language = data['language']
            favourites = data['favourites']

            if data['description']:
                description = await remove_html(data['description'])
                if len(description) > 1024:
                    description = description[0:1020] + '...'
            else:
                description = '*Ingen biografi funnet* 😔'

            featured_in = []
            for media in data['staffMedia']['edges']:
                if media['node']['isAdult'] is True:
                    nsfwtag = ' (NSFW)'
                else:
                    nsfwtag = ''
                media_name = media['node']['title']['romaji']
                media_url = media['node']['siteUrl']
                media_role = media['staffRole']
                featured_in.append(f'[{media_name}]({media_url}){nsfwtag}\n{media_role}')
            featured_in = '\n\n'.join(featured_in)

            characters = []
            for character in data['characters']['edges']:
                character_url = character['node']['siteUrl']
                character_name = character['node']['name']['full']
                if character['node']['name']['native'] != ' ' and character['node']['name']['native'] is not None:
                    character_name += ' (' + character['node']['name']['native'] + ')'
                characters.append(f'[{character_name}]({character_url})')
            characters = '\n\n'.join(characters)

            embed = discord.Embed(color=0x02A9FF, title=name_romaji, url=url, description=name_native)
            embed.set_thumbnail(url=image)
            embed.add_field(name='Antall favoritter på Anilist', value=favourites, inline=False)
            embed.add_field(name='Biografi', value=description, inline=False)
            if characters != '':
                embed.add_field(name='Har vært stemmen til bl.a.', value=characters, inline=False)
            if featured_in != '':
                embed.add_field(name='Har deltatt i produksjonen av bl.a.', value=featured_in, inline=False)
            embed = embed_templates.default_footer(ctx, embed)
            await ctx.send(embed=embed)

    @commands.bot_has_permissions(embed_links=True)
    @commands.cooldown(1, 5, commands.BucketType.guild)
    @commands.command()
    async def studio(self, ctx, *, studionavn: str):
        """Viser informasjon om et animestudio"""

        async with ctx.channel.typing():

            query = '''
                query ($search: String) {
                    Studio(search: $search) {
                        name
                        siteUrl
                        favourites
                        media(sort: POPULARITY_DESC, perPage: 3) {
                        nodes {
                            siteUrl
                            coverImage {
                                large
                            }
                            isAdult
                            title {
                            romaji
                            }
                        }
                        }
                    }
                    }
                '''
            variables = {
                'search': studionavn
            }
            try:
                data = post('https://graphql.anilist.co', json={'query': query, 'variables': variables}).json()
                data = data['data']['Studio']
                url = data['siteUrl']
            except TypeError:
                embed = embed_templates.error_fatal('Kunne ikke finne studioet!')
                return await ctx.send(embed=embed)

            name = data['name']
            favourites = data['favourites']

            popular_media = []
            for media in data['media']['nodes']:
                if media['isAdult'] is True:
                    nsfwtag = ' (NSFW)'
                else:
                    nsfwtag = ''
                media_name = media['title']['romaji']
                media_url = media['siteUrl']
                popular_media.append(f'- [{media_name}]({media_url}){nsfwtag}')
            popular_media = '\n'.join(popular_media)

            query2 = '''
                query ($search: String) {
                    Studio(search: $search) {
                        media(sort: START_DATE_DESC) {
                        nodes {
                            siteUrl
                            status
                            isAdult
                            title {
                            romaji
                            }
                        }
                        }
                    }
                    }
                '''
            data = post('https://graphql.anilist.co', json={'query': query2, 'variables': variables}).json()
            data = data['data']['Studio']

            recent_media = []
            upcoming_media = []
            for media in data['media']['nodes']:
                if media['isAdult'] is True:
                    nsfwtag = ' (NSFW)'
                else:
                    nsfwtag = ''
                media_name = media['title']['romaji']
                media_url = media['siteUrl']
                if media['status'] == 'NOT_YET_RELEASED':
                    upcoming_media.append(f'- [{media_name}]({media_url}){nsfwtag}')
                else:
                    recent_media.append(f'- [{media_name}]({media_url}){nsfwtag}')
            recent_media = '\n'.join(recent_media[0:3])
            upcoming_media = '\n'.join(upcoming_media[0:3])

            embed = discord.Embed(color=0x02A9FF, title=name, url=url)
            embed.add_field(name='Antall favoritter på Anilist', value=favourites, inline=False)
            if popular_media != '':
                embed.add_field(name='Mest Populære Anime', value=popular_media, inline=False)
            if recent_media != '':
                embed.add_field(name='Nyeste Utgitte Anime', value=recent_media, inline=False)
            if upcoming_media != '':
                embed.add_field(name='Kommende Anime', value=upcoming_media, inline=False)
            embed = embed_templates.default_footer(ctx, embed)
            await ctx.send(embed=embed)


async def setup(bot):
    await bot.add_cog(Anime(bot))
