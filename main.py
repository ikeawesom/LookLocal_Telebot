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


def reset_edits():
	global myp_desc, myp_price, myp_colour, myp_size, myp_product, myp_user
	myp_desc = False
	myp_price = False
	myp_colour = False
	myp_size = False
	myp_product = None
	myp_user = None


def reset_filters():
	global filtersSet, writingPrices
	filtersSet = {"colours": [], "sizes": [], "ranges": []}
	writingPrices = False


def reset_search():
	global searchSeller, exploring, current_cat
	searchSeller = False
	exploring = False
	current_cat = None


def reset_proc():

	# LISTING PROC
	reset_sell()

	# SEARCHING SELLER
	reset_search()

	# FILTERS
	reset_filters()

	# EDIT PRODUCTS
	reset_edits()


# ==================== ESSENTIAL VARIABLES ==================== #

PROD_KEY = os.environ["API_KEY_PROD"]
PUB_KEY = os.environ["API_KEY"]
API_KEY = PROD_KEY  # change when necessary

BOT_NAME = "Chaewon"
error_msg = "An error has occured. Please use /start to reset me!"
CURRENT_USER = ""

# Reset DB
# resetDB()

# DB Lists
member_lst = db["members"]
product_lst = db["products"]
print("Member Count:", len(member_lst))
for member in member_lst:
	print("Name:", member)
	member_prods = []
	for prod in member_lst[member]["products"]:
		member_prods.append(prod)
	print("Products:", ','.join(member_prods))
	print("Favourites:", member_lst[member]["favourites"])
	print("Bought:", member_lst[member]["bought"])
	print("Account created on:", member_lst[member]["creation"])
	print("\n")
print("=" * 100)
print("Product Count", len(product_lst))
for item in product_lst:
	print("Name:", item)
	print("Desc:", product_lst[item]['desc'])
	print("Category:", product_lst[item]['category'])
	print("Colour:", product_lst[item]["colour"])
	print("Size:", product_lst[item]["size"])
	print("Price:", product_lst[item]["price"])
	print("Filepath:", product_lst[item]["filepath"])
	print("Owner:", product_lst[item]["owner"])
	print("\n" + "-" * 50)
# print("Current Products", product_lst)

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
sellColour = get_Texts("start_sell")[4]
sellColour_bool = False
sellSize = get_Texts("start_sell")[5]
sellSize_bool = False
sellPic = get_Texts("start_sell")[6]
sellPrice_bool = False
sellPrice = get_Texts("start_sell")[7]
sellEnd = get_Texts("start_sell")[8]

# Exploring products
searchSeller = False
exploring = False
current_cat = None

# Filters
filtersSet = {"colours": [], "sizes": [], "ranges": []}
writingPrices = False

# Edit Products
myp_desc = False
myp_price = False
myp_colour = False
myp_size = False
myp_product = None
myp_user = None
# ==================== INLINE MARKUPS ==================== #

intro_buttons = [
 [InlineKeyboardButton("Explore Products 🔍", callback_data="START_explore")],
 [
  InlineKeyboardButton("Start Selling Products 💸", callback_data="START_sell")
 ], [InlineKeyboardButton("My Products 📦", callback_data="START_products")],
 [InlineKeyboardButton("Send Us Feedback ✉️", url="https://bit.ly/3IyuCov")]
]

selling_colour_buttons = [
 [
  InlineKeyboardButton("Red", callback_data="SELL_COLOUR_red"),
  InlineKeyboardButton("Orange", callback_data="SELL_COLOUR_orange")
 ],
 [
  InlineKeyboardButton("Yellow", callback_data="SELL_COLOUR_yellow"),
  InlineKeyboardButton("Green", callback_data="SELL_COLOUR_green")
 ],
 [
  InlineKeyboardButton("Blue", callback_data="SELL_COLOUR_blue"),
  InlineKeyboardButton("Purple", callback_data="SELL_COLOUR_purple")
 ], [InlineKeyboardButton("Others", callback_data="SELL_COLOUR_others")]
]

selling_sizes_buttons = [
 [InlineKeyboardButton("XS - below 6 years", callback_data="SELL_SIZE_XS")],
 [InlineKeyboardButton("S - 6 to 10 years", callback_data="SELL_SIZE_S")],
 [InlineKeyboardButton("M - 11 to 16 years", callback_data="SELL_SIZE_M")],
 [InlineKeyboardButton("L - 17 to 21 years", callback_data="SELL_SIZE_L")],
 [InlineKeyboardButton("XL - above 21 years", callback_data="SELL_SIZE_XL")]
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

explore_colour_buttons = [
 [
  InlineKeyboardButton("Red", callback_data="EXPLORE_FILTERS_Colours_red"),
  InlineKeyboardButton("Orange",
                       callback_data="EXPLORE_FILTERS_Colours_orange")
 ],
 [
  InlineKeyboardButton("Yellow",
                       callback_data="EXPLORE_FILTERS_Colours_yellow"),
  InlineKeyboardButton("Green", callback_data="EXPLORE_FILTERS_Colours_green")
 ],
 [
  InlineKeyboardButton("Blue", callback_data="EXPLORE_FILTERS_Colours_blue"),
  InlineKeyboardButton("Purple",
                       callback_data="EXPLORE_FILTERS_Colours_purple")
 ],
 [
  InlineKeyboardButton("Others",
                       callback_data="EXPLORE_FILTERS_Colours_others")
 ]
]

explore_sizes_buttons = [
 [
  InlineKeyboardButton("XS - below 6 years",
                       callback_data="EXPLORE_FILTERS_Sizes_XS")
 ],
 [
  InlineKeyboardButton("S - 6 to 10 years",
                       callback_data="EXPLORE_FILTERS_Sizes_S")
 ],
 [
  InlineKeyboardButton("M - 11 to 16 years",
                       callback_data="EXPLORE_FILTERS_Sizes_M")
 ],
 [
  InlineKeyboardButton("L - 17 to 21 years",
                       callback_data="EXPLORE_FILTERS_Sizes_L")
 ],
 [
  InlineKeyboardButton("XL - above 21 years",
                       callback_data="EXPLORE_FILTERS_Sizes_XL")
 ]
]

filter_buttons = [[
 InlineKeyboardButton("Colours", callback_data="EXPLORE_FILTERS_Colours"),
 InlineKeyboardButton("Sizes", callback_data="EXPLORE_FILTERS_Sizes"),
 InlineKeyboardButton("Price Range", callback_data="EXPLORE_FILTERS_Prices")
],
                  [
                   InlineKeyboardButton("Start Filtering",
                                        callback_data="EXPLORE_FILTERS_Finish")
                  ]]

explore_buttons = [
 # [
 #  InlineKeyboardButton("Your favourites ⭐ ", callback_data="EXPLORE_favourite")
 # ], [InlineKeyboardButton("HOT PRODUCTS 🔥", callback_data="EXPLORE_hot")],
 [InlineKeyboardButton("See All Products 🛒", callback_data="EXPLORE_all")],
 [
  InlineKeyboardButton("Male Tops 👕", callback_data="EXPLORE_maleTops"),
  InlineKeyboardButton("Male Bottoms 👖", callback_data="EXPLORE_maleBots")
 ],
 [
  InlineKeyboardButton("Female Tops 👚", callback_data="EXPLORE_femaleTops"),
  InlineKeyboardButton("Female Bottoms 🩳", callback_data="EXPLORE_femaleBots")
 ],
 [InlineKeyboardButton("Dresses 👗", callback_data="EXPLORE_dresses")],
 [
  InlineKeyboardButton("Accessories 🧢", callback_data="EXPLORE_access"),
  InlineKeyboardButton("Hoodies/Jackets 🧥", callback_data="EXPLORE_hoodies")
 ],
 [
  InlineKeyboardButton("Search by Seller 🔍",
                       callback_data="EXPLORE_searchSeller")
 ],
 [InlineKeyboardButton("<< Back", callback_data="BACK_start")]
]

print()


# ==================== HANDLERS ==================== #
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):

	reset_proc()
	
	global CURRENT_USER
	# Logs bot starting
	cur_time = datetime.now()
	cur_id = update.message.chat.id
	cur_user = update.message.chat.username
	CURRENT_USER = cur_user
	print(f"{cur_time}: {cur_user} ({cur_id}) started the bot")

	reply_markup = InlineKeyboardMarkup(intro_buttons)

	# Resets selling procedure
	reset_sell()

	# Checks if new user
	global intro_txt
	if str(cur_user) in member_lst:
		intro_txt = f"Welcome back <b>{cur_user}</b>, it's {BOT_NAME} here again!\n\nWhat can I do for you today?"
		await context.bot.send_message(chat_id=update.effective_chat.id,
		                               text=intro_txt,
		                               reply_markup=reply_markup,parse_mode="HTML")
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
	global sellName_bool, sellDesc_bool, sellCat_bool, sellPic_bool, sellPrice_bool, writingPrices, searchSeller, exploring

	# response = "Procedure has not begun. Invalid use of stop command.\n\n"
	# if sellName_bool or sellDesc_bool or sellCat_bool or sellPic_bool or sellPrice_bool or writingPrices:
	reset_proc()
	response = "All procedures stopped.\n\n"
	reply_markup = InlineKeyboardMarkup(intro_buttons)
	await context.bot.send_message(chat_id=update.effective_chat.id,
	                               text=response + "What else can I do for you?",
	                               reply_markup=reply_markup)


async def setFilters(update: Update, context: ContextTypes.DEFAULT_TYPE):
	global filtersSet, exploring
	if not (exploring):
		await context.bot.send_message(
		 chat_id=update.effective_chat.id,
		 text=
		 "You are currently not exploring any products. Please use /start to explore products to use this filters command."
		)
		return

	reply_markup = InlineKeyboardMarkup(filter_buttons)
	colours = str(", ".join(filtersSet["colours"]))
	sizes = str(", ".join(filtersSet["sizes"]))
	prices = ", ".join(filtersSet["ranges"])
	await context.bot.send_message(
	 chat_id=update.effective_chat.id,
	 text=
	 f"Current filters:\nColours: {colours}\nSizes: {sizes}\n{prices}\nSelect some filters to choose from.",
	 reply_markup=reply_markup)


async def clearFilters(update: Update, context: ContextTypes.DEFAULT_TYPE):
	global filtersSet
	filtersSet = {"colours": [], "sizes": [], "ranges": []}
	await context.bot.send_message(
	 chat_id=update.effective_chat.id,
	 text="Your search filters have now been cleared.")


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
	text = update.message.text
	cur_user = update.message.chat.username

	global temp_product, sellName_bool, sellDesc_bool, sellCat_bool, sellPic_bool, sellPrice_bool, sellEnd_bool, searchSeller, writingPrices, filtersSet, myp_product, myp_desc, myp_price, myp_colour, myp_size, myp_user

	# EDIT PRODUCT LISTING
	if myp_product != None:
		if myp_desc:
			db["products"][myp_product]['desc'] = text
			db["members"][myp_user]["products"][myp_product]['desc'] = text
			await update.message.reply_text(
			 f"Successfully updated description for <b>{myp_product}</b>.",parse_mode="HTML")
			myp_desc = False
		elif myp_price:
			item_price = text
			if not (item_price.isdigit()):
				await update.message.reply_text("Please enter a valid price in SGD.")
				return
			db["products"][myp_product]['price'] = text
			db["members"][myp_user]["products"][myp_product]['price'] = text
			await update.message.reply_text(
			 f"Successfully updated price for <b>{myp_product}</b>.",parse_mode="HTML")
			myp_price = False
		elif myp_colour:
			db["products"][myp_product]['colour'] = text
			db["members"][myp_user]["products"][myp_product]['colour'] = text
			await update.message.reply_text(
			 f"Successfully updated colour description for <b>{myp_product}</b>.",parse_mode="HTML")
			myp_colour = False
		elif myp_size:
			db["products"][myp_product]['size'] = text
			db["members"][myp_user]["products"][myp_product]['size'] = text
			await update.message.reply_text(
			 f"Successfully updated size for <b>{myp_product}</b>.",parse_mode="HTML")
			myp_size = False

		myp_product = None
		myp_user = None

		return

	# EXPLORE PRODUCTS SEARCHING
	if searchSeller:
		if text in db["members"]:
			product_lst = db["members"][text]["products"]
			if len(product_lst > 0):
				await update.message.reply_text(
				 f"Found 'em! Here are the product(s) listed by user @{text}.")
				for product in product_lst:
					name = product
					desc = product_lst[product]["desc"]
					filepath = product_lst[product]["filepath"]
					price = product_lst[product]["price"]
					size = product_lst[product]["size"]
					caption = f"<b>{name}</b>\n\n{desc}\n\n---\n<b>Size: </b>{size}\n<b>Selling Price:</b> SGD{price}\n\nListed by @{text}"

					await context.bot.send_photo(chat_id=update.effective_chat.id,
					                             photo=filepath,
					                             caption=caption,
					                             parse_mode="HTML")
				return
		reply_markup = InlineKeyboardMarkup(intro_buttons)
		await context.bot.send_message(
		 chat_id=update.effective_chat.id,
		 text=
		 f"My apologies, the user @{text} does not have any products listed.\n\nWhat else can I do for you?",
		 reply_markup=reply_markup)

		searchSeller = False
		return

	# FILTERS: PRICE RANGE
	if writingPrices:
		if "," in text:
			text = text.split(",")
			if len(text) == 2 and text[0].isdigit() and text[1].isdigit():
				filtersSet["ranges"].append(f"{text[0]} - {text[1]}")
				colours = str(", ".join(filtersSet["colours"]))
				sizes = str(", ".join(filtersSet["sizes"]))
				prices = ", ".join(filtersSet["ranges"])
				reply_markup = InlineKeyboardMarkup(filter_buttons)
				await context.bot.send_message(
				 chat_id=update.effective_chat.id,
				 text=
				 f"Current filters:\nColours: {colours}\nSizes: {sizes}\n{prices}\nSelect some filters to choose from.",
				 reply_markup=reply_markup)
			writingPrices = False

		else:
			await update.message.reply_text(
			 "Invalid input. Filtering process has stopped.")
			writingPrices = False

	# LISTING STATEMENTS
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
		photo = update.message.photo
		if not (photo):
			await update.message.reply_text("Please choose a proper photo.")
			return
		file_id = photo[-2].file_id
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
		reply_markup = InlineKeyboardMarkup(intro_buttons)
		await update.message.reply_text(
		 sellEnd + f" @{cur_user}!\n\nIs there anything else I can do for you?",
		 reply_markup=reply_markup)

		# UPDATE REPLIT DB
		item_name = temp_product["name"]

		print(temp_product)

		# Saves photo to replit
		user_path = os.path.join(os.getcwd(), f"products/{cur_user}")

		if not (os.path.isdir(user_path)):
			os.mkdir(os.path.join(user_path))

		await temp_product["photo"].download_to_drive(
		 os.path.join(user_path, f"{item_name}.jpg"))

		# Users DB
		details = {
		 'desc': temp_product["desc"],
		 'colour': temp_product['colour'],
		 'size': temp_product['size'],
		 'price': temp_product["price"],
		 'filepath': os.path.join(user_path, f"{item_name}.jpg")
		}
		db["members"][str(cur_user)]["products"][item_name] = details

		details_products = {
		 'owner': cur_user,
		 'desc': temp_product["desc"],
		 'category': temp_product["category"],
		 'colour': temp_product['colour'],
		 'size': temp_product['size'],
		 'price': temp_product["price"],
		 'filepath': os.path.join(user_path, f"{item_name}.jpg")
		}

		db["products"][item_name] = details_products

		temp_product = {}  # reset temp_product dictionary

		# Log
		print(f"{cur_user} has listed a new item '{item_name}'.")


async def queryHandler(update: Update, context: ContextTypes.DEFAULT_TYPE):
	global exploring, current_cat, filtersSet
	query = update.callback_query
	await query.answer()

	mainQuery = query.data.split("_")
	prefix = mainQuery[0]
	option = mainQuery[1]

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

		elif option == 'products':  # User wants to view their products
			global CURRENT_USER
			exploring = False
			cur_user = CURRENT_USER
			product_lst = db["members"][cur_user]["products"]

			if len(product_lst) > 0:
				myproducts_buttons = []
				for product in product_lst:
					temp_format = [
					 InlineKeyboardButton(product,
					                      callback_data=f"MYPRODUCTS_{cur_user}_{product}")
					]
					myproducts_buttons.append(temp_format)

				reply_markup = InlineKeyboardMarkup(myproducts_buttons)
				await context.bot.send_message(
				 chat_id=update.effective_chat.id,
				 text=f"Splendid! Here are the product(s) listed by you.",
				 reply_markup=reply_markup)

				return
			else:
				await context.bot.send_message(chat_id=update.effective_chat.id,
				                               text="You do not have any products listed.")
		else:
			await context.bot.send_message(chat_id=update.effective_chat.id,
			                               text=error_msg)

	# Viewing user's products options
	elif prefix == "MYPRODUCTS":
		exploring = False
		mainFilter = query.data.split("_")
		cur_user = mainFilter[1]
		product = mainFilter[2]

		# listing options for editing
		if len(mainFilter) == 3:

			product_options = [
			 [
			  InlineKeyboardButton(
			   "Edit Desc", callback_data=f"MYPRODUCTS_{cur_user}_{product}_desc"),
			  InlineKeyboardButton(
			   "Edit Price", callback_data=f"MYPRODUCTS_{cur_user}_{product}_price")
			 ],
			 [
			  InlineKeyboardButton(
			   "Edit Colour", callback_data=f"MYPRODUCTS_{cur_user}_{product}_colour"),
			  InlineKeyboardButton(
			   "Edit Size", callback_data=f"MYPRODUCTS_{cur_user}_{product}_size")
			 ],
			 [
			  InlineKeyboardButton(
			   "Remove Listing",
			   callback_data=f"MYPRODUCTS_{cur_user}_{product}_remove")
			 ]
			]

			reply_markup = InlineKeyboardMarkup(product_options)
			await query.edit_message_text(f"What would you like to do with <b>{product}</b>?",parse_mode="HTML")
			await query.edit_message_reply_markup(reply_markup)
			return
			
		# Editing options
		selected_option = mainFilter[3]

		global myp_desc, myp_price, myp_colour, myp_size, myp_product, myp_user

		myp_product = mainFilter[2]
		myp_user = cur_user
		if selected_option == "desc":
			await context.bot.send_message(
			 chat_id=update.effective_chat.id,
			 text=
			 f"Please tell me the updated description for your product: <b>{myp_product}</b>.",parse_mode="HTML")
			myp_desc = True
		elif selected_option == "price":
			await context.bot.send_message(
			 chat_id=update.effective_chat.id,
			 text=
			 f"Please tell me the updated price for your product: <b>{myp_product}</b>.",parse_mode="HTML")
			myp_price = True
		elif selected_option == "colour":
			await context.bot.send_message(
			 chat_id=update.effective_chat.id,
			 text=
			 f"Please tell me the updated colour for your product: <b>{myp_product}</b>.",parse_mode="HTML")
			myp_colour = True
		elif selected_option == "size":
			await context.bot.send_message(
			 chat_id=update.effective_chat.id,
			 text=
			 f"Please tell me the updated size for your product: <b>{myp_product}</b>.",parse_mode="HTML")
			myp_size = True
		elif selected_option == "remove":
			delete_buttons = [[InlineKeyboardButton("YES",callback_data=f"MYPRODUCTS_{cur_user}_{product}_removeYES"),InlineKeyboardButton("NO",callback_data=f"MYPRODUCTS_{cur_user}_{product}_removeNO")]]
			reply_markup = InlineKeyboardMarkup(delete_buttons)
			await context.bot.send_message(
			 chat_id=update.effective_chat.id,
			 text=
			 f"Are you sure you want to remove this listing: <b>{myp_product}</b>? This cannot be undone!",reply_markup=reply_markup,parse_mode="HTML")

		# Remove listing
		else:
			reply_markup = InlineKeyboardMarkup(intro_buttons) 
			if selected_option == "removeYES":
				try:
					removed_item = db["products"].pop(myp_product)
					removed_item_user = db["members"][myp_user]["products"].pop(myp_product)
					print(f"Removed {removed_item} from DB")
					print(f"Removed {removed_item_user} from user DB")
					await query.edit_message_text(text=f"Your item <b>{myp_product}</b> has been removed. Is there anything else I can do for you?", reply_markup=reply_markup,parse_mode="HTML")
				except:
					await query.edit_message_text(text=f"Your listing <b>{myp_product}</b> has already been removed. Is there anything else I can do for you?", reply_markup=reply_markup,parse_mode="HTML")
			elif selected_option == "removeNO":
				await query.edit_message_text(text=f"Okay! I'll take you back to the start menu.", reply_markup=reply_markup)
					

		print(selected_option)

	# To add category for product listing
	elif prefix == "SELL":
		exploring = False
		global sellPic_bool, temp_product, sellCat_bool, sellSize_bool, sellColour_bool, sellPrice_bool

		if len(mainQuery) > 2:
			subSell = mainQuery[1]
			if subSell == "SIZE":
				temp_product["size"] = mainQuery[2]
				sellSize_bool = False
				sellPic_bool = True
				await context.bot.send_message(chat_id=update.effective_chat.id,
				                               text=sellPic)
			elif subSell == "COLOUR":
				temp_product["colour"] = mainQuery[2]
				sellColour_bool = False
				sellSize_bool = True
				reply_markup = InlineKeyboardMarkup(selling_sizes_buttons)
				await context.bot.send_message(chat_id=update.effective_chat.id,
				                               text=sellSize,
				                               reply_markup=reply_markup)
			return
		temp_product["category"] = option
		sellCat_bool = False
		sellColour_bool = True
		reply_markup = InlineKeyboardMarkup(selling_colour_buttons)
		await context.bot.send_message(chat_id=update.effective_chat.id,
		                               text=sellColour,
		                               reply_markup=reply_markup)

	# Back option functionalities
	elif prefix == "BACK":
		if option == "start":
			# Edits text and shows new keyboard markup
			await query.edit_message_text(text=intro_txt)
			reply_markup = InlineKeyboardMarkup(intro_buttons)
			await query.edit_message_reply_markup(reply_markup)

	# Exploring products functionality
	elif prefix == "EXPLORE":
		exploring = True
		product_lst = db["products"]

		# User chooses to view ALL products
		# TODO: Add page numbers
		async def filters_helper(mainFilter, query, category):
			if len(mainFilter) > 3:
				subFilter = mainFilter[3]
				filtersSet[category].append(subFilter)

				colours = str(", ".join(filtersSet["colours"]))
				sizes = str(", ".join(filtersSet["sizes"]))
				prices = ", ".join(filtersSet["ranges"])
				reply_markup = InlineKeyboardMarkup(filter_buttons)

				await query.edit_message_text(
				 text=
				 f"Current filters:\nColours: {colours}\nSizes: {sizes}\n{prices}\nSelect some filters to choose from."
				)
				await query.edit_message_reply_markup(reply_markup)
				return

		# Filters
		if option == "FILTERS":
			mainFilter = query.data.split("_")
			filterCat = mainFilter[2]

			if filterCat == "Colours":
				if len(mainFilter) > 3:
					await filters_helper(mainFilter, query, "colours")
					return

				await query.edit_message_text(text="Choose a colour you would like.")
				reply_markup = InlineKeyboardMarkup(explore_colour_buttons)
				await query.edit_message_reply_markup(reply_markup)

			elif filterCat == "Sizes":
				if len(mainFilter) > 3:
					await filters_helper(mainFilter, query, "sizes")
					return

				await query.edit_message_text(text="Select a size you want to check out.")
				reply_markup = InlineKeyboardMarkup(explore_sizes_buttons)
				await query.edit_message_reply_markup(reply_markup)

			elif filterCat == "Prices":
				global writingPrices

				await query.edit_message_text(
				 text=
				 "Tell me the minimum and maximum price you are looking for, seperated by a comma. <i>(E.g. 20,100)</i>",
				 parse_mode="HTML")
				writingPrices = True

			elif filterCat == "Finish":
				print("filters: ", filtersSet)
				# if current_cat == "all":
				count = 0

				for product in product_lst:
					print(product)
					print(current_cat)
					if current_cat != "all":
						if current_cat != product_lst[product]["category"]:
							continue

					name = product
					desc = product_lst[product]["desc"]
					filepath = product_lst[product]["filepath"]
					price = product_lst[product]["price"]
					owner = product_lst[product]["owner"]
					size = product_lst[product]["size"]
					caption = f"<b>{name}</b>\n\n{desc}\n\n---\n<b>Size: </b>{size}\n<b>Selling Price:</b> SGD{price}\n\nListed by @{owner}"

					if len(filtersSet['colours']) > 0:
						for colourFilter in filtersSet['colours']:
							colour = product_lst[product]["colour"]
							if colour == colourFilter:
								count += 1
								await context.bot.send_photo(chat_id=update.effective_chat.id,
								                             photo=filepath,
								                             caption=caption,
								                             parse_mode="HTML")
								continue

					if len(filtersSet['sizes']) > 0:
						for sizeFilter in filtersSet['sizes']:
							size = product_lst[product]["size"]
							if size == sizeFilter:
								count += 1
								await context.bot.send_photo(chat_id=update.effective_chat.id,
								                             photo=filepath,
								                             caption=caption,
								                             parse_mode="HTML")
								continue

					if len(filtersSet['ranges']) > 0:
						for rangeFilter in filtersSet['ranges']:
							minimum = int(rangeFilter.split("-")[0].strip())
							maximum = int(rangeFilter.split("-")[1].strip())

							if int(price) >= minimum and int(price) <= maximum:
								count += 1
								await context.bot.send_photo(chat_id=update.effective_chat.id,
								                             photo=filepath,
								                             caption=caption,
								                             parse_mode="HTML")
								continue

				if count == 0:
					await context.bot.send_message(
					 chat_id=update.effective_chat.id,
					 text=
					 "Oops, there are currently no products listed! Apologies for the inconvenience."
					)

		# Normal exploring
		elif option == "all":
			current_cat = option
			count = 0
			for product in product_lst:
				count += 1
				name = product
				desc = product_lst[product]["desc"]
				cat = product_lst[product]["category"]
				filepath = product_lst[product]["filepath"]

				price = product_lst[product]["price"]
				owner = product_lst[product]["owner"]
				size = product_lst[product]["size"]
				caption = f"<b>{name}</b>\n\n{desc}\n\n---\n<b>Size: </b>{size}\n<b>Selling Price:</b> SGD{price}\n\nListed by @{owner}"
				await context.bot.send_photo(chat_id=update.effective_chat.id,
				                             photo=filepath,
				                             caption=caption,
				                             parse_mode="HTML")

			if count == 0:
				await context.bot.send_message(
				 chat_id=update.effective_chat.id,
				 text=
				 "Oops, there are currently no products listed! Apologies for the inconvenience."
				)

		# User chooses to search products by seller
		elif option == "searchSeller":
			global searchSeller

			await context.bot.send_message(
			 chat_id=update.effective_chat.id,
			 text=
			 "Who is the seller you are looking for? Tell me their Telegram username!")
			searchSeller = True
		else:
			count = 0
			current_cat = option
			for product in product_lst:

				cat = product_lst[product]["category"]

				if option != cat:
					continue

				count += 1
				name = product
				desc = product_lst[product]["desc"]
				size = product_lst[product]["size"]
				filepath = product_lst[product]["filepath"]
				price = product_lst[product]["price"]
				owner = product_lst[product]["owner"]

				caption = f"<b>{name}</b>\n\n{desc}\n\n---\n<b>Size: </b>{size}\n<b>Selling Price:</b> SGD{price}\n\nListed by @{owner}"
				await context.bot.send_photo(chat_id=update.effective_chat.id,
				                             photo=filepath,
				                             caption=caption,
				                             parse_mode="HTML")

			if count == 0:
				await context.bot.send_message(
				 chat_id=update.effective_chat.id,
				 text=
				 "Oops, there are currently no products in this category! Try something else?"
				)


# ==================== STARTING BOT ==================== #

if __name__ == '__main__':

	application = ApplicationBuilder().token(API_KEY).build()

	# ASSIGNING HANDLERS
	start_handler = CommandHandler('start', start)
	stop_handler = CommandHandler('stop', stop)
	filters_handler = CommandHandler('setfilters', setFilters)
	clear_filters_handler = CommandHandler('clearfilters', clearFilters)
	message_handler = MessageHandler(filters.ALL, handle_message)
	query_handler = CallbackQueryHandler(queryHandler)

	# ADDING HANDLERS TO APPLICATION
	application.add_handler(start_handler)
	application.add_handler(stop_handler)
	application.add_handler(filters_handler)
	application.add_handler(clear_filters_handler)
	application.add_handler(message_handler)
	application.add_handler(query_handler)

	keep_alive()
	application.run_polling()
