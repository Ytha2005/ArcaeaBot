from nonebot import on_command, CommandSession,logger
import requests
import sqlite3

sqlite = sqlite3.connect('./data/data.db')
sqlite_cur = sqlite.cursor()
sqlite_cur.execute('''create table if not exists bind_data(
                    user_qq int primary key not null,
                    usercode text not null)''')
sqlite.commit()
logger.info('SQLite Init Success.')

def get_userinfo(usercode):
    url = 'https://arcapi.cirnobaka.moe/v3/'
    param = {'usercode' : str(usercode) , 'recent' : 'true'}
    header = {'User-Agent'}
    r = requests.get(url + 'userinfo',params=param, headers=header)
    return r.json()


def get_songinfo(songname):
    url = 'https://arcapi.cirnobaka.moe/v3/'
    param = {'songname' : str(songname)}
    header = {'User-Agent'}
    r = requests.get(url + 'songinfo',params=param, headers=header)
    return r.json()


@on_command('stat', only_to_me=False)
async def stat(session: CommandSession):
    try: usercode = session.args['usercode']
    except KeyError:
        return 
    userinfo = get_userinfo(usercode)['content']
    user_name = str(userinfo['name'])
    user_ptt = str(userinfo['rating']/100.0)
    recentsong = userinfo['recent_score']
    recentsong_name = str(recentsong['song_id'])
    recentsong_difficuly = str(recentsong['difficulty'])
    songinfo = get_songinfo(recentsong_name)['content']['difficulties'][int(recentsong_difficuly)]
    song_ptt = str(songinfo['ratingReal'])
    recentsong_score = str(recentsong['score'])
    recentsong_ptt = recentsong['rating']
    await session.send(user_name +'(' + user_ptt + ')' + '\n最近游玩曲目：' + recentsong_name +
    '\n该曲目分数：' + recentsong_score +
    '\n铺面定数：' + song_ptt +
    '\n游玩定数：' + '%.2f' % recentsong_ptt)

@on_command('bind', only_to_me=False)
async def bind(session: CommandSession):
    try: bindcode = session.args['bindcode']
    except KeyError: 
        return
    try:
        sqlite_cur.execute("insert into bind_data values(%d,'%s')" %
                        (session.event.user_id,bindcode))
        sqlite.commit()
        await session.send('绑定成功！')
    except sqlite3.IntegrityError:
        await session.send('你已经绑定过了⑧')

    cursor = sqlite_cur.execute("SELECT user_qq , usercode from bind_data")
    for row in cursor:
        print ("ID = "+str(row[0]))
        print ("NAME = "+str(row[1])+"\n")
    

@on_command('unbind', only_to_me=False)
async def unbind(session: CommandSession):
    sqlite_cur.execute("delete from bind_data where user_qq=%d " %
                        (session.event.user_id))
    sqlite.commit()
    await session.send('解绑成功！')
    # cursor = sqlite_cur.execute("SELECT user_qq , usercode from bind_data")
    # for row in cursor:
    #     print ("ID = "+str(row[0]))
    #     print ("NAME = "+str(row[1])+"\n")


@unbind.args_parser
async def _(session: CommandSession):
    return 


@bind.args_parser
async def _(session: CommandSession):
    stripped_arg = session.current_arg_text.strip()
    if stripped_arg.isdigit() and len(stripped_arg)==9:
        session.state['bindcode'] = stripped_arg
    else:
        await session.send('你管这叫好友代码？')
    return

@stat.args_parser
async def _(session: CommandSession):
    stripped_arg = session.current_arg_text.strip()
    
    if not stripped_arg:
        sqlite_cur.execute('select usercode from bind_data where user_qq = %d' % (session.event.user_id))
        data = sqlite_cur.fetchall()
        if data:
            session.state['usercode'] = data[0][0]
            return
        if not data:
            await session.send('你绑定了么?')
            return
    else:
        if stripped_arg.isdigit() and len(stripped_arg)==9:
            session.state['usercode'] = stripped_arg
            return
        else: 
            await session.send('你管这叫好友代码？')
    return
