import logging, os
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import filters, MessageHandler, ApplicationBuilder, CommandHandler, ContextTypes, CallbackQueryHandler
from datetime import datetime
from replit import db
from keep_alive import keep_alive

# Manage Logs
logging.basicConfig(
 format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
 level=logging.INFO)

# ==================== HELPER FUNCTIONS ==================== #


def get_Texts(category):
	filename = f"texts/{category}.txt"
	with open(filename, "r") as file:
		return file.read().strip().split(';')


def resetDB():
	db["members"] = {}
	db["products"] = {}


def reset_sell():
	global sellName_bool, sellDesc_bool, sellCat_bool, sellPic_bool, sellPrice_bool
	sellName_bool = False
	sellDesc_bool = False
	sellCat_bool = False
	sellPic_bool = False
	sellPrice_bool = False


# ==================== ESSENTIAL VARIABLES ==================== #

API_KEY = os.environ["API_KEY"]
BOT_NAME = "Tristan"
error_msg = "An error has occured. Please use /start to reset me!"

# Reset DB
# resetDB()

# DB Lists
member_lst = db["members"]
product_lst = db["products"]
print("Member Count:", len(member_lst))
print("Current Members:", member_lst)
print("Product Count", len(product_lst))
print("Current Products", product_lst)

# Get texts
intro_txt = get_Texts("intro")[0]
exploreStart_txt = get_Texts("start_explore")[0]

# Selling products
temp_product = {}
sellStart_txt = get_Texts("start_sell")[0]

sellName_bool = False
sellName = get_Texts("start_sell")[1]
sellDesc_bool = False
sellDesc = get_Texts("start_sell")[2]
sellCat_bool = False
sellCat = get_Texts("start_sell")[3]
sellPic_bool = False
sellPic = get_Texts("start_sell")[4]
sellPrice_bool = False
sellPrice = get_Texts("start_sell")[5]
sellEnd = get_Texts("start_sell")[6]

# ==================== INLINE MARKUPS ==================== #

intro_buttons = [
 [InlineKeyboardButton("Explore Products 🔍", callback_data="START_explore")],
 [
  InlineKeyboardButton("Start Selling Products 💸 ", callback_data="START_sell")
 ],
 [InlineKeyboardButton("Visit our Website 🌐 ", url="https://www.google.com")]
]

selling_buttons = [[
 InlineKeyboardButton("Male Tops 👕", callback_data="SELL_maleTops"),
 InlineKeyboardButton("Male Bottoms 👖", callback_data="SELL_maleBots")
],
                   [
                    InlineKeyboardButton("Female Tops 👚",
                                         callback_data="SELL_femaleTops"),
                    InlineKeyboardButton("Female Bottoms 🩳",
                                         callback_data="SELL_femaleBots")
                   ],
                   [
                    InlineKeyboardButton("Dresses 👗",
                                         callback_data="SELL_dresses")
                   ],
                   [
                    InlineKeyboardButton("Accessories 🧢",
                                         callback_data="SELL_access"),
                    InlineKeyboardButton("Hoodies/Jackets 🧥",
                                         callback_data="SELL_hoodies")
                   ]]

explore_buttons = [
 [
  InlineKeyboardButton("Your favourites ⭐ ", callback_data="EXPLORE_favourite")
 ], [InlineKeyboardButton("HOT PRODUCTS 🔥", callback_data="EXPLORE_hot")],
 [InlineKeyboardButton("See All Products 🛒", callback_data="EXPLORE_all")],
 [
  InlineKeyboardButton("Male Tops 👕", callback_data="EXPLORE_maleTops"),
  InlineKeyboardButton("Male Bottoms 👖", callback_data="EXPLORE_maleBots")
 ],
 [
  InlineKeyboardButton("Female Tops 👚", callback_data="EXPLORE_femaleTops"),
  InlineKeyboardButton("Female Bottoms 🩳", callback_data="EXPLORE_femaleBots")
 ], [InlineKeyboardButton("Dresses 👗", callback_data="EXPLORE_dresses")],
 [
  InlineKeyboardButton("Accessories 🧢", callback_data="EXPLORE_access"),
  InlineKeyboardButton("Hoodies/Jackets 🧥", callback_data="EXPLORE_hoodies")
 ], [InlineKeyboardButton("<< Back", callback_data="BACK_start")]
]


# ==================== HANDLERS ==================== #
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):

	# Logs bot starting
	cur_time = datetime.now()
	cur_id = update.message.chat.id
	cur_user = update.message.chat.username
	print(f"{cur_time}: {cur_user} ({cur_id}) started the bot")

	reply_markup = InlineKeyboardMarkup(intro_buttons)

	# Resets selling procedure
	reset_sell()

	# Checks if new user
	global intro_txt
	if str(cur_user) in member_lst:
		intro_txt = f"Welcome back {cur_user}, it's {BOT_NAME} here again!\n\nWhat can I do for you today?"
		await context.bot.send_message(chat_id=update.effective_chat.id,
		                               text=intro_txt,
		                               reply_markup=reply_markup)
	else:
		new_member_items = {
		 'products': {},
		 'favourites': {},
		 'bought': {},
		 'creation': str(cur_time)
		}

		member_lst[cur_user] = new_member_items
		db["members"] = member_lst

		await context.bot.send_message(chat_id=update.effective_chat.id,
		                               text=f"Hi there {cur_user}! 👋\n\n" +
		                               intro_txt,
		                               reply_markup=reply_markup)


async def stop(update: Update, context: ContextTypes.DEFAULT_TYPE):
	global sellName_bool, sellDesc_bool, sellCat_bool, sellPic_bool, sellPrice_bool

	response = "Listing procedure has not begun. Invalid use of stop command.\n\n"
	if sellName_bool or sellDesc_bool or sellCat_bool or sellPic_bool or sellPrice_bool:
		reset_sell()
		response = "Listing procedure has stopped.\n\n"
	reply_markup = InlineKeyboardMarkup(intro_buttons)
	await context.bot.send_message(
	 chat_id=update.effective_chat.id,
	 text=response+"What else can I do for you?",
	 reply_markup=reply_markup)


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
	text = update.message.text
	photo = update.message.photo
	cur_user = update.message.chat.username

	global temp_product, sellName_bool, sellDesc_bool, sellCat_bool, sellPic_bool, sellPrice_bool, sellEnd_bool
	if sellName_bool:
		if text in db["members"][str(cur_user)]["products"]:
			await update.message.reply_text(
			 "You already have one product as that name. Please pick a new one.")
			return
		item_name = text
		temp_product["name"] = item_name
		sellName_bool = False
		sellDesc_bool = True
		await update.message.reply_text(sellDesc)
	elif sellDesc_bool:
		item_desc = text
		temp_product["desc"] = item_desc
		sellDesc_bool = False
		sellCat_bool = True

		# Set up reply markup
		reply_mark = InlineKeyboardMarkup(selling_buttons)

		await update.message.reply_text(sellCat, reply_markup=reply_mark)
	elif sellPic_bool:
		if not (photo):
			await update.message.reply_text("Please choose a proper photo.")
			return
		file_id = photo[0].file_id
		photo_file = await context.bot.get_file(file_id)
		temp_product["photo"] = photo_file
		sellPic_bool = False
		sellPrice_bool = True
		await update.message.reply_text(sellPrice)
	elif sellPrice_bool:
		item_price = text
		if not (item_price.isdigit()):
			await update.message.reply_text("Please enter a valid price in SGD.")
			return
		temp_product["price"] = item_price
		sellPrice_bool = False
		await update.message.reply_text(sellEnd + f" @{cur_user}!")

		# UPDATE REPLIT DB
		item_name = temp_product["name"]

		# Saves photo to replit
		user_path = os.path.join(os.getcwd(), f"products//{cur_user}")

		if not (os.path.isdir(user_path)):
			os.mkdir(os.path.join(user_path))

		await temp_product["photo"].download_to_drive(
		 os.path.join(user_path, f"{item_name}.jpg"))

		# Users DB
		details = {'desc': temp_product["desc"], 'price': temp_product["price"]}
		db["members"][str(cur_user)]["products"][item_name] = details

		details_products = {
		 'owner': cur_user,
		 'desc': temp_product["desc"],
		 'category': temp_product["category"],
		 'price': temp_product["price"],
		 'filepath': os.path.join(user_path, f"{item_name}.jpg")
		}
		db["products"][item_name] = details_products

		temp_product = {}  # reset temp_product dictionary

		# Log
		print(f"{cur_user} has listed a new item '{item_name}'.")


async def queryHandler(update: Update, context: ContextTypes.DEFAULT_TYPE):

	query = update.callback_query
	await query.answer()

	prefix = query.data.split("_")[0]
	option = query.data.split("_")[1]

	# FROM START

	if prefix == "START":
		if option == "explore":  # if user wants to explore products

			# Set up inlinekeyboardbuttons
			reply_markup = InlineKeyboardMarkup(explore_buttons)

			# Edits text and shows new keyboard markup
			await query.edit_message_text(text=exploreStart_txt)
			await query.edit_message_reply_markup(reply_markup)

		elif option == "sell":  # If user wants to sell products
			global sellName_bool
			await context.bot.send_message(chat_id=update.effective_chat.id,
			                               text=sellStart_txt)
			await context.bot.send_message(chat_id=update.effective_chat.id,
			                               text=sellName)
			sellName_bool = True

		else:
			await context.bot.send_message(chat_id=update.effective_chat.id,
			                               text=error_msg)
	# To add category for product listing
	elif prefix == "SELL":
		global sellPic_bool, temp_product, sellCat_bool
		temp_product["category"] = option
		sellCat_bool = False
		sellPic_bool = True
		await context.bot.send_message(chat_id=update.effective_chat.id,
		                               text=sellPic)

	# Back option functionalities
	elif prefix == "BACK":
		if option == "start":
			# Edits text and shows new keyboard markup
			await query.edit_message_text(text=intro_txt)
			reply_markup = InlineKeyboardMarkup(intro_buttons)
			await query.edit_message_reply_markup(reply_markup)


# ==================== STARTING BOT ==================== #

if __name__ == '__main__':

	application = ApplicationBuilder().token(API_KEY).build()

	# ASSIGNING HANDLERS
	start_handler = CommandHandler('start', start)
	stop_handler = CommandHandler('stop', stop)
	message_handler = MessageHandler(filters.ALL, handle_message)
	query_handler = CallbackQueryHandler(queryHandler)

	# ADDING HANDLERS TO APPLICATION
	application.add_handler(start_handler)
	application.add_handler(stop_handler)
	application.add_handler(message_handler)
	application.add_handler(query_handler)

	keep_alive()
	application.run_polling()
