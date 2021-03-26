from discord.ext import commands
import discord

from os import remove

from cogs.utils import embed_templates, misc_utils


class Info(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.bot_has_permissions(embed_links=True, external_emojis=True)
    @commands.guild_only()
    @commands.cooldown(1, 2, commands.BucketType.guild)
    @commands.command(aliases=['guildinfo', 'server', 'serverinfo', 'si', 'gi'])
    async def guild(self, ctx):
        """
        Viser info om guilden
        """

        guild_created_date = ctx.guild.created_at.strftime('%d. %b. %Y - %H:%M')
        since_created_days = (ctx.message.created_at - ctx.guild.created_at).days

        if since_created_days == 1:
            since_created_days_string = 'dag'
        else:
            since_created_days_string = 'dager'

        total_members = ctx.guild.member_count
        bot_members = 0
        online_members = 0
        idle_members = 0
        dnd_members = 0
        offline_members = 0
        for member in ctx.guild.members:
            if member.bot:
                bot_members += 1
            if str(member.status) == 'online':
                online_members += 1
            elif str(member.status) == 'idle':
                idle_members += 1
            elif str(member.status) == 'dnd':
                dnd_members += 1
            elif str(member.status) == 'offline':
                offline_members += 1

        roles = []
        for role in ctx.guild.roles:
            if role.name != '@everyone':
                roles.append(role.name)
        roles.reverse()
        roles = ', '.join(roles)
        if len(roles) > 1024:
            roles = f'Skriv `{self.bot.prefix}guildroller` for å se rollene'
        if roles == '':
            roles = '**Ingen roller**'

        boosters = []
        premium_subscribers = sorted(
            ctx.guild.premium_subscribers, key=lambda m: m.premium_since)
        for booster in premium_subscribers:
            boosters.append(f'{booster.name}#{booster.discriminator}')
        boosters = ', '.join(boosters)
        if len(boosters) > 1024:
            boosters = f'Skriv `{self.bot.prefix}boosters` for å se boosters'
        if boosters == '':
            boosters = '**Ingen boosters**'

        text_channels = len(ctx.guild.text_channels)
        voice_channels = len(ctx.guild.voice_channels)
        categories = len(ctx.guild.categories)
        total_channels = text_channels + voice_channels

        flags = {
            'us': ':flag_us:',
            'eu': ':flag_eu:',
            'singapore': ':flag_sg:',
            'london': ':flag_gb:',
            'sydney': ':flag_au:',
            'amsterdam': ':flag_nl:',
            'frankfurt': ':flag_de:',
            'brazil': ':flag_br:',
            'dubai': ':flag_ae:',
            'japan': ':flag_jp:',
            'russia': ':flag_ru:',
            'southafrica': ':flag_za:',
            'hongkong': ':flag_hk:',
            'india': ':flag_in:'
        }
        region = str(ctx.guild.region)
        if region.startswith('us'):
            region = 'us'
        elif region.startswith('eu'):
            region = 'eu'
        elif region.startswith('amsterdam'):
            region = 'amsterdam'
        try:
            flag = flags[region]
        except KeyError:
            flag = ':question:'

        region_names = {
            'eu-central': 'Sentral-Europa',
            'eu-west': 'Vest-Europa',
            'europe': 'Europa',
            'hongkong': 'Hong Kong',
            'russia': 'Russland',
            'southafrica': 'Sør-Afrika',
            'us-central': 'Midt-USA',
            'us-east': 'New Jersey',
            'us-south': 'Sør-USA',
            'us-west': 'California',
            'vip-amsterdam': 'Amsterdam (VIP)',
            'vip-us-east': 'Øst-USA (VIP)',
            'vip-us-west': 'Vest-USA (VIP)',
        }
        try:
            region_name = region_names[str(ctx.guild.region)]
        except KeyError:
            region_name = str(ctx.guild.region).title()

        features_string = ''
        if ctx.guild.features is not []:
            features = {
                'VIP_REGIONS': 'VIP',
                'VANITY_URL': 'Egen URL',
                'INVITE_SPLASH': 'Invitasjonsbilde',
                'VERIFIED': 'Verifisert',
                'PARTNERED': 'Discord Partner',
                'MORE_EMOJI': 'Ekstra emoji',
                'DISCOVERABLE': 'Fremhevet',
                'FEATURABLE': 'Kan fremheves',
                'COMMUNITY': 'Sammfunsguild',
                'COMMERCE': 'Butikkanaler',
                'PUBLIC': 'Offentlig guild',
                'NEWS': 'Nyhetskanaler',
                'BANNER': 'Banner',
                'ANIMATED_ICON': 'Animert ikon',
                'PUBLIC_DISABLED': 'Ikke offentlig',
                'WELCOME_SCREEN_ENABLED': 'Velkomstvindu',
                'PREVIEW_ENABLED': 'Forhåndsvisning',
                'MEMBER_VERIFICATION_GATE_ENABLED': 'Medlemsverifisering'
            }
            for feature in ctx.guild.features:
                features_string += f'{features[feature]}\n'

        photos = {}
        if ctx.guild.splash_url:
            photos['Invitasjonsbilde'] = ctx.guild.splash_url_as(format='png')
        if ctx.guild.banner_url:
            photos['Banner'] = ctx.guild.banner_url_as(format='png')

        verification_level = {
            'none': 'ingen',
            'low': 'e-post',
            'medium': 'e-post, registrert i 5 min',
            'high': 'e-post, registrert i 5 min, medlem i 10 min',
            'extreme': 'telefon'
        }
        verification = verification_level[str(ctx.guild.verification_level)]

        content_filter = {
            'disabled': 'nei',
            'no_role': 'for alle uten rolle',
            'all_members': 'ja'
        }
        content = content_filter[str(ctx.guild.explicit_content_filter)]

        embed = discord.Embed(color=ctx.me.color, description=f'**Verifiseringskrav:** {verification}\n' +
                                                              f'**Innholdsfilter:** {content}\n' +
                                                              f'**Boost Tier:** {ctx.guild.premium_tier}\n' +
                                                              f'**Emoji:** {len(ctx.guild.emojis)}')
        embed.set_author(name=ctx.guild.name, icon_url=ctx.guild.icon_url)
        embed.set_thumbnail(url=ctx.guild.icon_url_as(static_format='png'))
        embed.add_field(name='ID', value=ctx.guild.id)
        embed.add_field(name='Eier', value=ctx.guild.owner.mention)
        embed.add_field(name='Region', value=f'{flag} {region_name}')
        embed.add_field(name='Opprettet', value=f'{guild_created_date}\n{since_created_days} ' +
                                                f'{since_created_days_string} siden')
        embed.add_field(name=f'Kanaler ({total_channels})', value=f'💬 Tekst: **{text_channels}**\n' +
                                                                  f'🔊 Tale: **{voice_channels}**\n' +
                                                                  f'🗃️ Kategorier: **{categories}**')
        embed.add_field(name=f'Medlemmer ({total_members})',
                        value=f'👤 Mennesker: **{int(total_members) - int(bot_members)}**\n' +
                              f'🤖 Båtter: **{bot_members}**\n' +
                              f'{self.bot.emoji["online"]}{online_members} ' +
                              f'{self.bot.emoji["idle"]}{idle_members} ' +
                              f'{self.bot.emoji["dnd"]}{dnd_members} ' +
                              f'{self.bot.emoji["offline"]}{offline_members}')
        embed.add_field(name=f'Roller ({len(ctx.guild.roles) - 1})', value=roles, inline=False)
        if ctx.guild.premium_tier != 0:
            embed.add_field(name=f'Boosters ({ctx.guild.premium_subscription_count})', value=boosters, inline=False)

        if features_string != '':
            embed.add_field(name='Tillegsfunksjoner', value=features_string)

        if photos != {}:
            photos_string = ''
            for key, value in photos.items():
                photos_string += f'[{key}]({value})\n'
            embed.add_field(name='Bilder', value=photos_string)
        await ctx.send(embed=embed)

    @commands.bot_has_permissions(embed_links=True)
    @commands.guild_only()
    @commands.cooldown(1, 2, commands.BucketType.guild)
    @commands.command(aliases=['serverroller', 'guildroles', 'serverroles'])
    async def guildroller(self, ctx):
        """
        Viser rollene i en guild
        """

        roles = []
        for role in ctx.guild.roles:
            if role.name != '@everyone':
                roles.append(role.name)
        if roles is []:
            roles = ['**Ingen Roller**']
        roles.reverse()
        roles = ', '.join(roles)

        roles = roles.replace(', --', '\n--')
        roles = roles.replace('--, ', '--\n')

        if len(roles) > 2048:
            with open(f'./assets/temp/{ctx.guild.id}_roles.txt', 'w') as f:
                f.seek(0)
                f.write(roles)

            txt_file = discord.File(f'./assets/temp/{ctx.guild.id}_roles.txt')
            await ctx.send(file=txt_file)

            with misc_utils.ignore_exception(OSError):
                remove(f'./assets/temp/{ctx.guild.id}_roles.txt')

            return

        if roles == '':
            roles = '**Ingen roller**'

        embed = discord.Embed(color=ctx.me.color, description=roles)
        embed.set_author(name=f'Roller ({len(ctx.guild.roles) - 1})', icon_url=ctx.guild.icon_url)
        embed.set_footer(text=ctx.guild.name, icon_url=ctx.guild.icon_url)
        await ctx.send(embed=embed)

    @commands.bot_has_permissions(embed_links=True)
    @commands.guild_only()
    @commands.cooldown(1, 2, commands.BucketType.guild)
    @commands.command(aliases=['guildboosters', 'serverboosters', 'boosts'])
    async def boosters(self, ctx):
        """
        Viser boosters i en guild
        """

        if len(ctx.guild.premium_subscribers) == 0:
            embed = embed_templates.error_warning(ctx, text='Serveren har ikke noen boosts :(')
            return await ctx.send(embed=embed)

        boosters = []
        premium_subscribers = sorted(ctx.guild.premium_subscribers, key=lambda m: m.premium_since)
        for booster in premium_subscribers:
            date = booster.premium_since.strftime('%d.%m.%Y %H:%M')
            boosters.append(f'{booster.name}#{booster.discriminator} - {date}')
        boosters = '\n'.join(boosters)

        embed = discord.Embed(color=ctx.me.color, description=boosters)
        embed.set_author(name=f'Boosters ({ctx.guild.premium_subscription_count})', icon_url=ctx.guild.icon_url)
        embed.set_footer(text=ctx.guild.name, icon_url=ctx.guild.icon_url)
        await ctx.send(embed=embed)

    @commands.bot_has_permissions(embed_links=True)
    @commands.guild_only()
    @commands.cooldown(1, 2, commands.BucketType.guild)
    @commands.command(aliases=['serverikon', 'servericon', 'guildicon', 'icon', 'guildikon'])
    async def ikon(self, ctx):
        """
        Viser ikonet til serveren du er i
        """

        url = ctx.guild.icon_url_as(static_format='png')

        embed = discord.Embed(color=ctx.me.color, description=f'[Lenke]({url})')
        embed.set_author(name=ctx.guild.name, icon_url=url)
        embed.set_image(url=url)
        embed = embed_templates.default_footer(ctx, embed)
        await ctx.send(embed=embed)

    @commands.bot_has_permissions(embed_links=True)
    @commands.guild_only()
    @commands.cooldown(1, 2, commands.BucketType.guild)
    @commands.command(aliases=['guildsplash', 'serversplash'])
    async def splash(self, ctx):
        """
        Viser invite splash til serveren
        """

        if not ctx.guild.splash_url:
            embed = embed_templates.error_warning(ctx, text='Serveren har ikke en splash')
            return await ctx.send(embed=embed)

        url = ctx.guild.splash_url_as(format='png')

        embed = discord.Embed(color=ctx.me.color, description=f'[Lenke]({url})')
        embed.set_author(name=ctx.guild.name, icon_url=ctx.guild.icon_url)
        embed.set_image(url=url)
        embed = embed_templates.default_footer(ctx, embed)
        await ctx.send(embed=embed)

    @commands.bot_has_permissions(embed_links=True)
    @commands.guild_only()
    @commands.cooldown(1, 2, commands.BucketType.guild)
    @commands.command(aliases=['guildbanner', 'serverbanner'])
    async def banner(self, ctx):
        """
        Viser invite splash til serveren
        """

        if not ctx.guild.banner_url:
            embed = embed_templates.error_warning(ctx, text='Serveren har ikke et banner :(')
            return await ctx.send(embed=embed)

        url = ctx.guild.banner_url_as(format='png')

        embed = discord.Embed(color=ctx.me.color, description=f'[Lenke]({url})')
        embed.set_author(name=ctx.guild.name, icon_url=ctx.guild.icon_url)
        embed.set_image(url=url)
        embed = embed_templates.default_footer(ctx, embed)
        await ctx.send(embed=embed)

    @commands.bot_has_permissions(embed_links=True, external_emojis=True)
    @commands.guild_only()
    @commands.cooldown(1, 2, commands.BucketType.guild)
    @commands.command(aliases=['userinfo', 'ui', 'brukerinfo', 'user'])
    async def bruker(self, ctx, *, bruker: discord.Member = None):
        """
        Viser info om en bruker
        """

        if not bruker:
            bruker = ctx.author

        app = ''
        if str(bruker.mobile_status) != 'offline':
            app += '📱 '
        if str(bruker.web_status) != 'offline':
            app += '🌐 '
        if str(bruker.desktop_status) != 'offline':
            app += '💻'

        join_index = sorted(ctx.guild.members, key=lambda m: m.joined_at).index(bruker) + 1
        creation_index = sorted(ctx.guild.members, key=lambda m: m.created_at).index(bruker) + 1
        if bruker.premium_since:
            premium_index = sorted(ctx.guild.premium_subscribers, key=lambda m: m.premium_since).index(bruker) + 1

        bruker_joined_date = bruker.joined_at.strftime('%d. %b. %Y - %H:%M')
        bruker_created_date = bruker.created_at.strftime('%d. %b. %Y - %H:%M')
        since_joined_days = (ctx.message.created_at - bruker.joined_at).days
        since_created_days = (ctx.message.created_at - bruker.created_at).days
        if since_created_days == 1:
            since_created_days_string = 'dag'
        else:
            since_created_days_string = 'dager'
        if since_joined_days == 1:
            since_joined_days_string = 'dag'
        else:
            since_joined_days_string = 'dager'

        if bruker.premium_since:
            premium_since = bruker.premium_since.strftime('%d. %b. %Y - %H:%M')
            premium_since_days = (ctx.message.created_at - bruker.premium_since).days
            if since_joined_days == 1:
                premium_since_days_string = 'dag'
            else:
                premium_since_days_string = 'dager'

        roles = []
        for role in bruker.roles:
            if role.name != '@everyone':
                roles.append(role.name)
        roles.reverse()
        roles = ', '.join(roles)

        if len(roles) > 1024:
            roles = f'Skriv `{self.bot.prefix}{ctx.command}` for å se rollene'
        if roles == '':
            roles = '**Ingen roller**'

        if str(bruker.color) != '#000000':
            color = bruker.color
        else:
            color = discord.Colour(0x99AAB5)

        statuses = {
            'online': f'{self.bot.emoji["online"]} Pålogget',
            'idle': f'{self.bot.emoji["idle"]} Inaktiv',
            'dnd': f'{self.bot.emoji["dnd"]} Ikke forstyrr',
            'offline': f'{self.bot.emoji["offline"]} Frakoblet'
        }
        status = statuses[str(bruker.status)]

        embed = discord.Embed(color=color, description=f'{bruker.mention}\nID: {bruker.id}\n{status}\n{app}')
        if bruker.display_name == bruker.name:
            embed.set_author(name=f'{bruker.name}#{bruker.discriminator}', icon_url=bruker.avatar_url)
        else:
            embed.set_author(name=f'{bruker.name}#{bruker.discriminator} | {bruker.display_name}',
                             icon_url=bruker.avatar_url)
        embed.set_thumbnail(url=bruker.avatar_url_as(static_format='png'))
        embed.add_field(name='Opprettet', value=f'{bruker_created_date}\n{since_created_days} ' +
                                                f'{since_created_days_string} siden')
        embed.add_field(name='Ble med i serveren', value=f'{bruker_joined_date}\n{since_joined_days} ' +
                                                         f'{since_joined_days_string} siden')
        if bruker.premium_since:
            embed.add_field(name='Boost', value=f'{premium_since}\n{premium_since_days} ' +
                                                f'{premium_since_days_string} siden\n' +
                                                f'Booster #{premium_index} av serveren', inline=False)
        embed.add_field(name=f'Roller ({len(bruker.roles) - 1})', value=roles, inline=False)
        embed.set_footer(text=f'#{join_index} Medlem av serveren | #{creation_index} Eldste brukeren på serveren')

        if bruker.activities:
            games = ''
            for activity in bruker.activities:
                games += f'{activity.name}\n'
            if games:
                embed.add_field(name='Spiller', value=games, inline=False)
        await ctx.send(embed=embed)

    @commands.bot_has_permissions(embed_links=True)
    @commands.guild_only()
    @commands.cooldown(1, 2, commands.BucketType.guild)
    @commands.command(aliases=['userroles'])
    async def brukerroller(self, ctx, bruker: discord.Member = None):
        """
        Viser rollene til en bruker
        """

        if not bruker:
            bruker = ctx.author

        roles = []
        for role in bruker.roles:
            if role.name != '@everyone':
                roles.append(role.name)
        roles.reverse()
        roles = ', '.join(roles)

        if len(roles) > 2048:
            txt_file = discord.File(f'./assets/temp/{ctx.guild.id}_{ctx.author.id}_roles.txt')
            await ctx.send(file=txt_file)

            with misc_utils.ignore_exception(OSError):
                remove(f'./assets/temp/{ctx.guild.id}_{ctx.author.id}_roles.txt')

            return

        if roles == '':
            roles = '**Ingen roller**'

        if str(bruker.color) != '#000000':
            color = bruker.color
        else:
            color = discord.Colour(0x99AAB5)

        embed = discord.Embed(color=color, description=roles)
        embed.set_author(name=f'Roller ({len(bruker.roles) - 1})', icon_url=bruker.avatar_url)
        embed.set_footer(text=f'{bruker.name}#{bruker.discriminator}', icon_url=bruker.avatar_url)
        await ctx.send(embed=embed)

    @commands.bot_has_permissions(embed_links=True)
    @commands.cooldown(1, 2, commands.BucketType.guild)
    @commands.command(aliases=['profilbilde', 'brukeravatar', 'useravatar'])
    async def avatar(self, ctx, bruker: discord.Member = None):
        """
        Viser avataren til en bruker
        """

        if not bruker:
            bruker = ctx.author

        if str(bruker.color) != '#000000':
            color = bruker.color
        else:
            color = discord.Colour(0x99AAB5)

        url = bruker.avatar_url_as(static_format='png')

        embed = discord.Embed(color=color, description=f'[Lenke]({url})')
        embed.set_author(name=f'{bruker.name}#{bruker.discriminator}', icon_url=url)
        embed.set_image(url=url)
        embed = embed_templates.default_footer(ctx, embed)
        await ctx.send(embed=embed)

    @commands.bot_has_permissions(embed_links=True)
    @commands.guild_only()
    @commands.cooldown(1, 2, commands.BucketType.guild)
    @commands.command(aliases=['roleinfo', 'rolleinfo'])
    async def rolle(self, ctx, *, rolle: discord.Role):
        """
        Viser info om en rolle
        """

        if rolle.name == '@everyone':
            embed = embed_templates.fatal(ctx, text='Skriv inn en annen rolle enn @everyone')
            return await ctx.send(embed=embed)

        if str(rolle.color) != '#000000':
            color = rolle.color
        else:
            color = discord.Colour(0x99AAB5)

        if rolle.mentionable:
            mentionable = 'Ja'
        else:
            mentionable = 'Nei'

        if rolle.hoist:
            hoisted = 'Ja'
        else:
            hoisted = 'Nei'

        rolle_created_date = rolle.created_at.strftime('%d. %b. %Y - %H:%M')
        since_created_days = (ctx.message.created_at - rolle.created_at).days

        if since_created_days == 1:
            since_created_days_string = 'dag'
        else:
            since_created_days_string = 'dager'

        members = []
        for member in rolle.members:
            members.append(f'{member.name}#{member.discriminator}')
        members = ', '.join(members)

        if len(members) > 1024:
            members = 'For mange medlemmer for å vise her'
        if len(members) == 0:
            members = '**Ingen**'

        permissions = ', '.join([permission for permission, value in iter(rolle.permissions) if value is True])

        embed = discord.Embed(title=rolle.name, description=f'{rolle.mention}\n**ID:** {rolle.id}', color=color)
        embed.set_author(name=rolle.guild.name, icon_url=rolle.guild.icon_url)
        embed.add_field(name='Fargekode', value=str(rolle.color))
        embed.add_field(name='Opprettet', value=f'{rolle_created_date}\n{since_created_days} ' +
                                                f'{since_created_days_string} siden')
        embed.add_field(name='Posisjon', value=rolle.position)
        embed.add_field(name='Nevnbar', value=mentionable)
        embed.add_field(name='Vises separat i medlemsliste', value=hoisted)
        if permissions:
            embed.add_field(name='Tillatelser', value=permissions, inline=False)
        embed.add_field(name=f'Brukere med rollen ({len(rolle.members)})', value=members, inline=False)
        embed = embed_templates.default_footer(ctx, embed)
        await ctx.send(embed=embed)

    @commands.bot_has_permissions(embed_links=True)
    @commands.guild_only()
    @commands.cooldown(1, 5, commands.BucketType.guild)
    @commands.command(aliases=['kanal', 'channel', 'channelinfo', 'textchannel'])
    async def tekstkanal(self, ctx, *, kanal: discord.TextChannel):
        """
        Viser info om en tekstkanal
        """

        nsfw = 'Nei'
        if kanal.is_nsfw():
            nsfw = 'Ja'

        if kanal.slowmode_delay == 0:
            saktemodus = 'Nei'
        else:
            saktemodus = f'Ja ({kanal.slowmode_delay} sekunder)'

        description = '**Ingen**'
        if kanal.topic:
            description = kanal.topic

        members = []
        for member in kanal.members:
            members.append(f'{member.name}#{member.discriminator}')
        members = ', '.join(members)
        if len(members) > 1024:
            members = 'For mange for å vise her'

        embed = discord.Embed(color=ctx.me.color, title=kanal.name, description=f'{kanal.mention}\nID: {kanal.id}')
        embed.set_author(name=kanal.guild.name, icon_url=kanal.guild.icon_url)
        embed.add_field(name='Beskrivelse', value=description, inline=False)
        embed.add_field(name='Opprettet', value=kanal.created_at.strftime('%d. %b. %Y - %H:%M'))
        embed.add_field(name='NSFW', value=nsfw)
        embed.add_field(name='Saktemodus', value=saktemodus)
        if kanal.category:
            embed.add_field(name='Kategori', value=kanal.category.name)
        embed.add_field(name=f'Antall med tilgang ({len(kanal.members)})', value=members)
        embed = embed_templates.default_footer(ctx, embed)
        await ctx.send(embed=embed)

    @commands.bot_has_permissions(embed_links=True)
    @commands.guild_only()
    @commands.cooldown(1, 5, commands.BucketType.guild)
    @commands.command(aliases=['talekanalinfo', 'voicechannel'])
    async def talekanal(self, ctx, *, kanal: discord.VoiceChannel):
        """
        Viser info om en talekanal
        """

        if kanal.user_limit == 0:
            limit = '∞ personer'
        else:
            limit = f'{kanal.user_limit} personer'

        embed = discord.Embed(color=ctx.me.color, title=kanal.name, description=f'ID: {kanal.id}')
        embed.set_author(name=kanal.guild.name, icon_url=kanal.guild.icon_url)
        embed.add_field(name='Opprettet', value=kanal.created_at.strftime('%d. %b. %Y - %H:%M'))
        embed.add_field(name='Bitrate', value=f'{int(kanal.bitrate / 1000)}kbps')
        embed.add_field(name='Maksgrense', value=limit)
        if kanal.category:
            embed.add_field(name='Kategori', value=kanal.category.name)
        embed.add_field(name='Antall koblet til', value=len(kanal.members))
        embed = embed_templates.default_footer(ctx, embed)
        await ctx.send(embed=embed)

    @commands.bot_has_permissions(embed_links=True)
    @commands.guild_only()
    @commands.cooldown(1, 5, commands.BucketType.guild)
    @commands.command(aliases=['emote'])
    async def emoji(self, ctx, emoji: discord.Emoji):
        """
        Viser info om en CUSTOM emoji som tilhører serveren
        """

        animated = 'Nei'
        if emoji.animated:
            animated = 'Ja'

        emoji = await emoji.guild.fetch_emoji(emoji.id)
        try:
            emoji_creator = f'{emoji.user.mention}\n{emoji.user.name}#{emoji.user.discriminator}'
        except AttributeError:
            emoji_creator = 'Jeg trenger `manage_emojis`-tillatelsen på serveren den er fra for å hente dette'

        embed = discord.Embed(color=ctx.me.color, title=emoji.name, description=f'ID: {emoji.id}')
        embed.set_author(name=emoji.guild.name, icon_url=emoji.guild.icon_url)
        embed.add_field(name='Opprettet', value=emoji.created_at.strftime('%d. %b. %Y - %H:%M'))
        embed.add_field(name='Animert', value=animated)
        embed.add_field(name='Lagt til av', value=emoji_creator)
        embed.set_image(url=emoji.url)
        embed = embed_templates.default_footer(ctx, embed)
        await ctx.send(embed=embed)

    @commands.bot_has_permissions(embed_links=True)
    @commands.guild_only()
    @commands.cooldown(1, 5, commands.BucketType.guild)
    @commands.command(aliases=['serveremoji', 'serveremotes'])
    async def guildemoji(self, ctx):
        """
        Viser alle emoji som serveren har
        """

        embed = discord.Embed(colour=ctx.me.color)
        embed.set_author(name=ctx.guild.name, icon_url=ctx.guild.icon_url)

        emoji_string = ''
        for emoji in ctx.guild.emojis:
            if len(emoji_string) > 2000:
                embed.description = emoji_string
                await ctx.send(embed=embed)
                emoji_string = ''
            emoji_string += f'{emoji} '

        embed.description = emoji_string
        await ctx.send(embed=embed)

    @commands.bot_has_permissions(embed_links=True)
    @commands.guild_only()
    @commands.cooldown(1, 5, commands.BucketType.guild)
    @commands.command(aliases=['oldest'])
    async def eldst(self, ctx, side=0):
        """
        Liste over de eldste brukerene på serveren
        """

        members = sorted(ctx.guild.members, key=lambda m: m.created_at)

        formatted_members = []
        for member in members:
            member_created_date = member.created_at.strftime('%d. %b. %Y - %H:%M')
            member_index = (members.index(member) + 1)
            formatted_members.append(
                f'**#{member_index}** {member.name}#{member.discriminator} - {member_created_date}'
            )

        page_data = misc_utils.paginator(formatted_members, int(side))
        side = page_data['page']
        pagecount = page_data['pagecount']
        members = '\n'.join(page_data['page_content'])

        embed = discord.Embed(color=ctx.me.color)
        embed.add_field(name='Eldste Discordbrukerene på serveren', value=members)
        embed.set_footer(text=f'Side: {side}/{pagecount}')
        await ctx.send(embed=embed)

    @commands.bot_has_permissions(embed_links=True)
    @commands.guild_only()
    @commands.cooldown(1, 5, commands.BucketType.guild)
    @commands.command()
    async def joinorder(self, ctx, side=0):
        """
        Liste over de første medlemmene av serveren
        """

        members = sorted(ctx.guild.members, key=lambda m: m.joined_at)

        formatted_members = []
        for member in members:
            member_joined_date = member.joined_at.strftime('%d. %b. %Y - %H:%M')
            member_index = (members.index(member) + 1)
            formatted_members.append(f'**#{member_index}** {member.name}#{member.discriminator} - {member_joined_date}')

        page_data = misc_utils.paginator(formatted_members, int(side))
        side = page_data['page']
        pagecount = page_data['pagecount']
        members = '\n'.join(page_data['page_content'])

        embed = discord.Embed(color=ctx.me.color)
        embed.set_author(name=ctx.guild.name, icon_url=ctx.guild.icon_url)
        embed.add_field(name='Første Discordbrukerene på serveren', value=members)
        embed.set_footer(text=f'Side: {side}/{pagecount}')
        await ctx.send(embed=embed)


def setup(bot):
    bot.add_cog(Info(bot))
