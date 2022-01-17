# import asyncio
# import discord
# from discord.ext import commands
# from discord.ext.commands.core import has_permissions
# from discord.ext.commands.errors import RoleNotFound


# class Roles(commands.Cog):
#     def __init__(self, bot):
#         self.bot = bot
#         self.default_role = None

#     def get_default_role_help_embed(ctx: commands.Context):
#         help_title = ":books: | О команде `!default_role`"
#         help_description = "> Устанавливает роль, которая выдается новым участникам"

#         help_embed = discord.Embed(
#             title=help_title, description=help_description, color=discord.Color.from_rgb(106, 118, 238))
#         help_embed.add_field(
#             name="Шаблон", value=f"> `!default_role Роль`", inline=False)
#         help_embed.add_field(
#             name="Пример", value=f"> `!default_role @Wanderer`", inline=False)
#         help_embed.set_footer(
#             icon_url=ctx.author.avatar_url, text=str(ctx.author))
#         return help_embed

#     def get_default_role_no_role_error_embed(ctx: commands.Context):
#         title_error = ":x: | Неточность"
#         mode_error = "Аргумент **default_role** должен обозначать роль для новичков\n\
#             Например, `@Wanderer`"
#         mode_error_embed = discord.Embed(
#             title=title_error, description=mode_error, color=discord.Color.red())
#         mode_error_embed.set_footer(
#             icon_url=ctx.author.avatar_url, text=str(ctx.author))
#         return mode_error_embed

#     def get_default_role_embed(ctx: commands.Context, role: discord.Role):
#         description = f"**Новая роль:** {role.mention}"
#         embed = discord.Embed(
#             title=f":rocket: | Установлена новая роль для новичков", description=description, color=discord.Color.green())
#         return embed

#     @commands.command()
#     @has_permissions(manage_roles=True)
#     async def default_role(self, ctx: commands.Context, role: discord.Role = None):
#         if role is None:
#             bot_answer = await ctx.send(embed=Roles.get_default_role_help_embed(ctx))
#         else:
#             self.default_role = role
#             bot_answer = await ctx.send(embed=Roles.get_default_role_embed(ctx, role))
#         await ctx.message.delete()
#         await asyncio.sleep(5)
#         await bot_answer.delete()

#     @default_role.error
#     async def default_role_error(self, ctx, error):
#         if isinstance(error, RoleNotFound):
#             bot_answer = await ctx.send(embed=Roles.get_default_role_no_role_error_embed(ctx))
#             await asyncio.sleep(5)
#             await bot_answer.delete()

#     def get_role_help_embed(ctx: commands.Context):
#         help_title = ":books: | О команде `!role`"
#         help_description = "> Выдает участникам новую роль"

#         help_embed = discord.Embed(
#             title=help_title, description=help_description, color=discord.Color.from_rgb(106, 118, 238))
#         help_embed.add_field(
#             name="Шаблон", value=f"> `!role Участники Роль`", inline=False)
#         help_embed.add_field(
#             name="Пример", value=f"> `!role @Wanderer @ONE OF THEM`", inline=False)
#         help_embed.set_footer(
#             icon_url=ctx.author.avatar_url, text=str(ctx.author))
#         return help_embed

#     def get_role_no_role_error_embed(ctx: commands.Context):
#         title_error = ":x: | Неточность"
#         mode_error = "Аргумент **role** должен обозначать существующую роль\n\
#             Например, `@Wanderer`"
#         mode_error_embed = discord.Embed(
#             title=title_error, description=mode_error, color=discord.Color.red())
#         mode_error_embed.set_footer(
#             icon_url=ctx.author.avatar_url, text=str(ctx.author))
#         return mode_error_embed

#     def get_role_embed(ctx: commands.Context, member: discord.Member, role: discord.Role):
#         description = f"**Новая роль:** {role.mention}"
#         description += f"**Модератор:** {str(ctx.author)}"
#         embed = discord.Embed(
#             title=f":rocket: | Установлена новая роль для {str(member)}", description=description, color=discord.Color.green())
#         return embed

#     @commands.command()
#     @has_permissions(manage_roles=True)
#     async def role(self, ctx: commands.Context, members: discord.Role = None, role: discord.Role = None):
#         if members is None:
#             bot_answer = await ctx.send(embed=Roles.get_role_help_embed(ctx))
#         elif role is None:
#             bot_answer = await ctx.send(embed=Roles.get_role_no_role_error_embed(ctx))
#         else:
#             bot_answer = await ctx.send(embed=Roles.get_role_embed(ctx, role))
#         await ctx.message.delete()
#         await asyncio.sleep(5)
#         await bot_answer.delete()

#     @role.error
#     async def role_error(self, ctx, error):
#         if isinstance(error, RoleNotFound):
#             bot_answer = await ctx.send(embed=Roles.get_role_no_role_error_embed(ctx))
#             await asyncio.sleep(5)
#             await bot_answer.delete()

#     @commands.Cog.listener()
#     async def on_member_join(self, member):
#         if member.bot:
#             return
#         await member.add_roles(self.default_role)


# async def setup_roles(bot):
#     bot.add_cog(Roles(bot))
