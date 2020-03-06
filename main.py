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
sh_RECORD = gc.open('botTest').worksheet("Day1")

# Bot Online & Load User Data Form
@client.event
async def on_ready():
	ids = sh_ID.col_values(1)
	dcs = sh_ID.col_values(2)
	for i in range(len(ids)-1):
		if i<len(dcs):
			dc_dict[dcs[i]] = ids[i];
	print("Bot is Ready")

# ID.Data List Update
@client.command(aliases = ['Update', 'UPDATE'])
async def update(ctx):
	ids = sh_ID.col_values(1)
	dcs = sh_ID.col_values(2)
	for i in range(len(ids)-1):
		if i<len(dcs):
			dc_dict[dcs[i]] = ids[i];

	await ctx.send('```ID List Updated.```')

# Discord ID binding
@client.command(aliases = ['Bind', 'BIND'])
async def bind(ctx):
	inArr = str(ctx.message.content).split()
	if len(inArr) == 2:
		if dc_dict.get(str(ctx.message.author)) == None:
			dc_dict[str(ctx.message.author)] = inArr[1]
			returnCell = sh_ID.find(inArr[1])
			sh_ID.update_cell(returnCell.row, returnCell.col+1, str(ctx.message.author))
			await ctx.send(str(ctx.message.author.mention) + ' 已成功與'+ inArr[1] + '綁定')
		elif dc_dict.get(str(ctx.message.author)) == inArr[1]:
			await ctx.send(str(ctx.message.author.mention) + ' 綁定過了拉')
		else:
			await ctx.send(str(ctx.message.author.mention) + ' 你已經與ID: '+ str(dc_dict[str(ctx.message.author)] + '綁定，欲更換ID請先解除綁定。'))
	else:
		await ctx.send("Syntax Error. !bind <遊戲ID>")

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
	if len(inArr) == 3:
		await ctx.send(str(ctx.message.author.mention) + ' 成績填寫完畢。\n對' + inArr[1] + '王造成' + inArr[2] + '傷害')
	elif len(inArr) == 4:
		await ctx.send(str(ctx.message.author.mention) + ' 成績填寫完畢, 返還：' + inArr[3])
	else:
		await ctx.send('Syntax Error. !fill <週目-王> <傷害> <返還秒數>')	
	# Clear DMG Field after filling scores
	returnCell = sh_DMG.find(dc_dict[str(ctx.message.author)])
	sh_DMG.update_cell(returnCell.row, 2, 'FALSE')
	# Clear input
	for i in range(3,5):
		sh_DMG.update_cell(returnCell.row, i, '')
	for i in range(6,9):	
		sh_DMG.update_cell(returnCell.row, i, 'FALSE')
	sh_DMG.update_cell(returnCell.row, 9, '')

# Damage filling for others

# Shift Sheet
@client.command()
async def ss(ctx):
	inArr = str(ctx.message.content).split()
	await ctx.send('Worksheet switch to Day' + inArr[1])


# prevent syntax error & 代刀操作
# Regist
@client.command(aliases = ['報', '報名'])
async def reg(ctx):
	returnCell = sh_DMG.find(dc_dict[str(ctx.message.author)])
	sh_DMG.update_cell(returnCell.row, returnCell.col+1, 'TRUE')
	for i in range(3,5):
		sh_DMG.update_cell(returnCell.row, i, '')
	for i in range(6,9):	
		sh_DMG.update_cell(returnCell.row, i, 'FALSE')
	sh_DMG.update_cell(returnCell.row, 9, '')
	await ctx.send(str(ctx.message.author.mention) + ', 已報名。')

# de-Regist
@client.command(aliases = ['退'])
async def dereg(ctx):
	returnCell = sh_DMG.find(dc_dict[str(ctx.message.author)])
	sh_DMG.update_cell(returnCell.row, 2, 'FALSE')
	# Clear input
	for i in range(3,5):
		sh_DMG.update_cell(returnCell.row, i, '')
	for i in range(6,9):	
		sh_DMG.update_cell(returnCell.row, i, 'FALSE')
	sh_DMG.update_cell(returnCell.row, 9, '')
	await ctx.send(str(ctx.message.author.mention) + ', 已退刀，你打得爛死。')

# DMG report
@client.command(aliases = ['卡'])
async def stop(ctx):
	inArr = str(ctx.message.content).split()
	returnCell = sh_DMG.find(dc_dict[str(ctx.message.author)])
	sh_DMG.update_cell(returnCell.row, 3, inArr[1])
	sh_DMG.update_cell(returnCell.row, 4, inArr[2])
	sh_DMG.update_cell(returnCell.row, 9, inArr[3])
	await ctx.send(str(ctx.message.author.mention) + ', 已完成回報傷害。')

# Overview
@client.command(aliases = ['Status'])
async def status(ctx):
	resultList = sh_DMG.findall("TRUE")

client.run(token)