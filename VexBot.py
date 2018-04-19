import asyncio,discord
from discord.ext.commands import Bot
from requests import get
from urllib.parse import urlencode as ue

Client = Bot('=')
token='BOT TOKEN HERE'
prefix='-'
matchDict={1:'P',2:'Q',3:'QF',4:'SF',5:'F'}

def teamEmbed(data):
    embed=discord.Embed(title=data['number'],description=data['team_name'],color=0xd9272e)
    embed.add_field(name='City',value=data['city'],inline=True)
    embed.add_field(name='Region',value=data['region'],inline=True)
    embed.add_field(name='Country',value=data['country'],inline=True)
    embed.add_field(name='Organisation',value=data['organisation'],inline=True)
    embed.add_field(name='Grade',value=data['grade'],inline=True)
    return embed

def rankEmbed(data):
    event=eval(get('https://api.vexdb.io/v1/get_events?sku='+data['sku']).content)['result'][0]['name']
    embed=discord.Embed(title=data['team'],description=event+' - '+data['division'],color=0xd9272e)
    embed.add_field(name='Rank',value=data['rank'],inline=False)
    embed.add_field(name='Wins',value=data['wins'],inline=True)
    embed.add_field(name='Losses',value=data['losses'],inline=True)
    embed.add_field(name='Ties',value=data['ties'],inline=True)
    embed.add_field(name='WP',value=data['wp'],inline=True)
    embed.add_field(name='AP',value=data['ap'],inline=True)
    embed.add_field(name='SP',value=data['sp'],inline=True)
    return embed

def matchEmbed(data):
    event=eval(get('https://api.vexdb.io/v1/get_events?sku='+data['sku']).content)['result'][0]['name']
    if data['round']>2:
        match='{} {}-{}'.format(matchDict[data['round']],data['instance'],data['matchnum'])
    else:
        match='{} {}'.format(matchDict[data['round']],data['matchnum'])
    teams=[[data['red1'],data['red2'],data['red3']],[data['blue1'],data['blue2'],data['blue3']]]
    if not teams[0][2]: teams[0][2]='N/A'
    if not teams[1][2]: teams[1][2]='N/A'
    embed=discord.Embed(title=event+' - '+data['division'],description=match,color=0xd9272e)
    embed.add_field(name='Red 1',value=teams[0][0],inline=True)
    embed.add_field(name='Red 2',value=teams[0][1],inline=True)
    embed.add_field(name='Red 3',value=teams[0][2],inline=True)
    if data['scored']:embed.add_field(name='Red Score',value=data['redscore'],inline=False)
    embed.add_field(name='Blue 1',value=teams[1][0],inline=True)
    embed.add_field(name='Blue 2',value=teams[1][1],inline=True)
    embed.add_field(name='Blue 3',value=teams[1][2],inline=True)
    if data['scored']:embed.add_field(name='Blue Score',value=data['bluescore'],inline=False)
    return embed

def teamsEmbed(data,sku):
    event=eval(get('https://api.vexdb.io/v1/get_events?sku='+sku).content)['result'][0]['name']
    embeds=[]
    embed=discord.Embed(title='Team List',description=event,color=0xd9272e)
    j=0
    for i in data:
        if j==25:
            embeds.append(embed.to_dict())
            j=0
            embed=discord.Embed(title=i['number'],description=i['team_name'],color=0xd9272e)
        else:
            embed.add_field(name=i['number'],value=i['team_name'],inline=False)
            j+=1
    embeds.append(embed.to_dict())        
    return embeds

@Client.event
async def on_ready():
    print('Invite link: https://discordapp.com/oauth2/authorize?client_id={}&scope=bot&permissions=8\n'.format(Client.user.id))
    embed=discord.Embed(title='Commands List',description='Make sure that "Allow DMs from server members" is enabled.',color=0xd9272e)
    embed.add_field(name=prefix+'team [team #]', value='Returns information about a team.', inline=False)
    embed.add_field(name=prefix+'rank [team #]', value='Returns rank information about a team in a competition.', inline=False)
    embed.add_field(name=prefix+'matches [team #]', value='Returns a list of matches for a team in a competition.', inline=False)
    embed.add_field(name=prefix+'teams', value='Returns a list of matches for a team in a competition.', inline=False)
    embed.add_field(name=prefix+'match', value='Returns the current match in a competition.', inline=False)
    embed.add_field(name=prefix+'scored', value='Returns the most recent scored match for a competition.', inline=False)
    embed.set_footer(text='Make sure that you enter commands in the appropriate channel for your competition.')
    comps=eval(get('https://api.vexdb.io/v1/get_events?status=current&country=United%20States').content)['result']
    info=discord.Embed(title='Welcome to VexBot',description='{} {} currently avaliable.'.format(len(comps),'competitions-'[:-((len(comps)==1)+1)]),color=0xd9272e)
    feedback=discord.Embed(title='Feedback',description='Please leave feedback to help improve this bot.',color=0xd9272e)
    feedback.add_field(name='Reddit',value='https://www.reddit.com/r/vex/comments/846262/vexbot_discord_server/',inline=False)
    feedback.add_field(name='VEX Forum',value='https://www.vexforum.com/index.php/32558-vexbot-discord-server',inline=False)
    feedback.add_field(name='Github',value='https://github.com/Trainmaster2/VexBot',inline=False)
    for server in Client.servers:
        everyone=server.default_role
        perms=everyone.permissions
        perms.send_messages=False
        Client.edit_role(server,everyone,permissions=perms)
        infoFound=False
        for i in list(server.channels).copy():
            if i.name=='info':
              await Client.purge_from(i)
              await Client.send_message(i,embed=info)
              await Client.send_message(i,embed=feedback)
              infoFound=True
              continue
            await Client.delete_channel(i)
        if not infoFound:
            channel=await Client.create_channel(server, 'Info', (everyone,discord.PermissionOverwrite(send_messages=False)))
            await Client.send_message(channel,embed=info)
            await Client.send_message(channel,embed=feedback)
        for i in comps:
            channel = await Client.create_channel(server,i['name'])
            await Client.edit_channel(channel,topic=i['sku'])
            await Client.send_message(channel,embed=embed)
        perms.send_messages=True
        Client.edit_role(server,everyone,permissions=perms)   

@Client.event
async def on_message(msg):
    if msg.server and msg.author.id!='422439927825825793':
        await Client.delete_message(msg)
        if msg.content.startswith(prefix):
            cmd=msg.content[len(prefix):].split()
            sku=msg.channel.topic
            if cmd[0]=='team':
                data=eval(get('https://api.vexdb.io/v1/get_teams?team='+cmd[1]).content)['result']
                if len(data)==1:
                    await Client.send_message(msg.author,embed=teamEmbed(data[0]))
                else:
                    await Client.send_message(msg.author,content='Could not find Team '+cmd[1].upper()+'.')
            if cmd[0]=='rank':
                data=eval(get('https://api.vexdb.io/v1/get_rankings?'+ue((('team',cmd[1]),('sku',sku)))).content)['result']
                if len(data)==1:
                    await Client.send_message(msg.author,embed=rankEmbed(data[0]))
                else:
                    await Client.send_message(msg.author,content='Could not find Team '+cmd[1].upper()+'.')
            if cmd[0]=='matches':
                data=eval(get('https://api.vexdb.io/v1/get_matches?'+ue((('team',cmd[1]),('sku',sku)))).content)['result']
                if len(data)>0:
                    for i in data:
                        await Client.send_message(msg.author,embed=matchEmbed(i))
                else:
                    await Client.send_message(msg.author,content='No matches found for Team '+cmd[1].upper()+'.')
            if cmd[0]=='match':
                data=eval(get('https://api.vexdb.io/v1/get_matches?scored=0&sku='+sku).content)['result']
                if len(data)>0:
                    await Client.send_message(msg.author,embed=matchEmbed(data[0]))
                else:
                    await Client.send_message(msg.author,content='No upcoming matches found.')
            if cmd[0]=='scored':
                data=eval(get('https://api.vexdb.io/v1/get_matches?scored=1&sku='+sku).content)['result']
                if len(data)>0:
                    await Client.send_message(msg.author,embed=matchEmbed(data[-1]))
                else:
                    await Client.send_message(msg.author,content='No scored matches found.')
            if cmd[0]=='teams':
                data=eval(get('https://api.vexdb.io/v1/get_teams?sku='+sku).content)['result']
                if len(data)>0:
                    for i in teamsEmbed(data,sku):
                        await Client.send_message(msg.author,embed=discord.Embed.from_data(i))
                else:
                    await Client.send_message(msg.author,content='No scored matches found.')

Client.run(token)
