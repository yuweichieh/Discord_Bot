import gspread
from oauth2client.service_account import ServiceAccountCredentials
import discord
from discord.ext import commands
from setup import *

dc_dict = {}
token = tkn()

client = commands.Bot(command_prefix = '!')
creds = crds()
gc = gspread.authorize(creds)

sh_ID = gc.open('botTest').worksheet("ID_List")
sh_DMG = gc.open('botTest').worksheet("集刀表")
# find的表單名稱不可英數混合 ex. Day1 -> X
sh_RECORD = gc.open('botTest').worksheet("1/1")

# Bot Online & Load User Data Form(Done)
@client.event
async def on_ready():
	ids = sh_ID.col_values(1)
	dcs = sh_ID.col_values(3)
	for i in range(len(ids)-1):
		if i<len(dcs):
			dc_dict[dcs[i]] = ids[i];
	print("Bot is Ready")

# ID.Data List Update(Done)
@client.command(aliases = ['Update', 'UPDATE'])
async def update(ctx):
	ids = sh_ID.col_values(1)
	dcs = sh_ID.col_values(3)
	for i in range(len(ids)-1):
		if i<len(dcs):
			dc_dict[dcs[i]] = ids[i];

	await ctx.send('```ID List Updated.```')

# Discord ID binding(Done)
@client.command(aliases = ['Bind', 'BIND'])
async def bind(ctx):
	inArr = str(ctx.message.content).split()
	if len(inArr) == 2:
		if dc_dict.get(str(ctx.message.author.id)) == None:
			try:
				resultCell = sh_ID.find(inArr[1])
				dc_dict[str(ctx.message.author.id)] = inArr[1]
				sh_ID.update_cell(resultCell.row, resultCell.col+1, str(ctx.message.author))
				sh_ID.update_cell(resultCell.row, resultCell.col+2, str(ctx.message.author.id))
				await ctx.send(str(ctx.message.author.mention) + ' 已成功與'+ inArr[1] + '綁定')
			except:
				await ctx.send(str(ctx.message.author.mention) + ' ID Not Found')
		elif dc_dict.get(str(ctx.message.author.id)) == inArr[1]:
			await ctx.send(str(ctx.message.author.mention) + ' 綁定過了拉')
		else:
			await ctx.send(str(ctx.message.author.mention) + ' 你已經與ID: '+ str(dc_dict[str(ctx.message.author.id)] + '綁定，欲更換ID請先解除綁定。'))
	else:
		await ctx.send("Syntax Error. !bind <遊戲ID>")

# Discord ID unbinding
@client.command(aliases = ['Unbind', 'UNBIND'])
async def unbind(ctx):
	await ctx.send(str(ctx.message.author.mention) + ' 已解除綁定')

# User manual -> !help
@client.command(aliases = ['Manual', 'man'])
async def manual(ctx):
	await ctx.send('```Current Commands:\
		\n\t表單名稱綁定: !bind <遊戲ID>\
		\n\t出刀傷害紀錄: !fill <週目-王> <傷害> <返還秒數>\
		\n\t集刀報名: !報\
		\n\t回報傷害: !卡 <傷害> <秒數> <備註>\
		\n\t退刀: !退```')

# UNDONE
# Damage filling
@client.command(aliases = ['FILL', 'Fill', '結'])
async def fill(ctx):
	inArr = str(ctx.message.content).split()

	resultCell = sh_RECORD.find(dc_dict[str(ctx.message.author.id)])
	# 1st Undone
	if sh_RECORD.cell(resultCell.row, 3).value == '':
		prefix = 3
	# 1st Return Undone
	elif sh_RECORD.cell(resultCell.row, 15).value == '' and sh_RECORD.cell(resultCell.row, 6).value == 'TRUE':
		prefix = 15
	# 2nd Undone
	elif sh_RECORD.cell(resultCell.row, 7).value == '':
		prefix = 7
	# 2nd Return Undone
	elif sh_RECORD.cell(resultCell.row, 18).value == '' and sh_RECORD.cell(resultCell.row, 10).value == 'TRUE':
		prefix = 18
	# 3rd Undone
	elif sh_RECORD.cell(resultCell.row, 11).value == '':
		prefix = 11
	# 3rd Return Undone
	elif sh_RECORD.cell(resultCell.row, 21).value == '' and sh_RECORD.cell(resultCell.row, 14).value == 'TRUE':
		prefix = 21

	if len(inArr) == 3:
		await ctx.send(str(ctx.message.author.mention) + ' 成績填寫。\n對' + inArr[1] + '王造成' + inArr[2] + '傷害')
	elif len(inArr) == 4 and (prefix == 3 or prefix == 7 or prefix == 11):
		sh_RECORD.update_cell(resultCell.row, prefix+3, "TRUE")
		await ctx.send(str(ctx.message.author.mention) + ' 成績填寫, \n對' + inArr[1] + '王造成' + inArr[2] + '傷害' + '\t返還：' + inArr[3])
	else:
		await ctx.send('Syntax Error. !fill <週目-王> <傷害> <返還秒數(Optional)>')
		return

	bossInfo = inArr[1].split("-")
	sh_RECORD.update_cell(resultCell.row, prefix+1, bossInfo[0])
	sh_RECORD.update_cell(resultCell.row, prefix+2, inArr[2])

	if(bossInfo[1] == '1'):
		sh_RECORD.update_cell(resultCell.row, prefix, "一王")
	elif(bossInfo[1] == '2'):
		sh_RECORD.update_cell(resultCell.row, prefix, "二王")
	elif(bossInfo[1] == '3'):
		sh_RECORD.update_cell(resultCell.row, prefix, "三王")
	elif(bossInfo[1] == '4'):
		sh_RECORD.update_cell(resultCell.row, prefix, "四王")
	elif(bossInfo[1] == '5'):
		sh_RECORD.update_cell(resultCell.row, prefix, "五王")


	# Clear DMG Field after filling scores
	resultCell = sh_DMG.find(dc_dict[str(ctx.message.author.id)])
	sh_DMG.update_cell(resultCell.row, 2, 'FALSE')
	for i in range(3,5):
		sh_DMG.update_cell(resultCell.row, i, '')
	for i in range(6,9):	
		sh_DMG.update_cell(resultCell.row, i, 'FALSE')
	sh_DMG.update_cell(resultCell.row, 9, '')

# Shift Sheet
@client.command()
async def ss(ctx):
	inArr = str(ctx.message.content).split()
	if len(inArr) == 2:
		inArr = str(ctx.message.content).split()
		ds = "Day" + inArr[1]
		sh_RECORD = gc.open('botTest').worksheet(ds)
		await ctx.send('Worksheet switch to Day' + inArr[1])
	else:
		await ctx.send('Syntax Error. !ss <Number of Day>')


# prevent syntax error & 代刀操作
# Regist
@client.command(aliases = ['報', '報名'])
async def reg(ctx):
	resultCell = sh_DMG.find(dc_dict[str(ctx.message.author.id)])
	sh_DMG.update_cell(resultCell.row, resultCell.col+1, 'TRUE')
	for i in range(3,5):
		sh_DMG.update_cell(resultCell.row, i, '')
	for i in range(6,9):	
		sh_DMG.update_cell(resultCell.row, i, 'FALSE')
	sh_DMG.update_cell(resultCell.row, 9, '')
	await ctx.send(str(ctx.message.author.mention) + ', 已報名。')

# de-Regist
@client.command(aliases = ['退'])
async def dereg(ctx):
	resultCell = sh_DMG.find(dc_dict[str(ctx.message.author.id)])
	sh_DMG.update_cell(resultCell.row, 2, 'FALSE')
	# Clear input
	for i in range(3,5):
		sh_DMG.update_cell(resultCell.row, i, '')
	for i in range(6,9):	
		sh_DMG.update_cell(resultCell.row, i, 'FALSE')
	sh_DMG.update_cell(resultCell.row, 9, '')
	await ctx.send(str(ctx.message.author.mention) + ', 已退刀，你打得爛死。')

# DMG report
@client.command(aliases = ['卡'])
async def stop(ctx):
	inArr = str(ctx.message.content).split()
	resultCell = sh_DMG.find(dc_dict[str(ctx.message.author.id)])
	sh_DMG.update_cell(resultCell.row, 3, inArr[1])
	sh_DMG.update_cell(resultCell.row, 4, inArr[2])
	sh_DMG.update_cell(resultCell.row, 9, inArr[3])
	await ctx.send(str(ctx.message.author.mention) + ', 已完成回報傷害。')

# Overview
@client.command(aliases = ['Status'])
async def status(ctx):
	resultList = sh_DMG.findall("TRUE")

client.run(token)