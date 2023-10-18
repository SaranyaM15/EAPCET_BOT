import pandas as pd
import telebot
from telebot import types
#from telegram import InlineKeyboardButton, InlineKeyboardMarkup
import time 
import threading 

# Create a Telebot instance
bot = telebot.TeleBot('6418379964:AAGGUWL63Y1gY-vYElPQTRbd0ATNMHiXR4Q')

#admin account chat ID
admin_user_id = 1656720679

# Constants for conversation states
GENDER, CASTE, BRANCH, RANK, RECOMMEND = range(5)

# Load  college dataset 
data_2023 = pd.read_csv('EAPCET_counseling_data_2023.csv')

user_data = {}

'''@bot.message_handler(commands=['admin'])
def admin_command(message):
    user_id = message.from_user.id

    if user_id in admin_user_id:
        # User is an admin, perform admin action
        bot.send_message(user_id, "This is an admin-only command.")
    else:
        # User is not an admin, send a message indicating restricted access
        bot.send_message(user_id, "You do not have permission to use this command.")'''

# Handle the /start command to initiate the conversation
@bot.message_handler(commands=['start'])
def start(message):
    markup = types.ReplyKeyboardRemove(selective=False)
    
    bot.send_message(message.chat.id, "Hi! I'm your EAPCET college recommendation bot. Let's get started.")
    bot.send_message(message.chat.id, "Please enter your gender (Male/Female):", reply_markup=markup)
    bot.register_next_step_handler(message, gender)

# Handle user input for gender
def gender(message):
    user_id = message.from_user.id
    Gen = message.text.strip().capitalize()
    # Continue to the next step (asking for caste) including error handling
    if Gen in ["Male", "Female"]:
        
        bot.send_message(user_id, "Enter your caste such that (BC_A,BC_B,BC_C,BC_D,BC_E,OC,SC,ST)")
        bot.send_message(user_id, " Now, please enter your caste:")
        bot.register_next_step_handler(message, lambda msg: caste(msg, Gen))
    else:
        bot.send_message(user_id, "Ivalid Input,Please enter Male or Female")
        bot.register_next_step_handler(message, gender)

branches_df = pd.read_excel('Branches.xlsx')

# Handle user input for caste
def caste(message,Gen):
    user_id = message.from_user.id
    Cas = message.text.strip().upper()
    # Continue to the next step (asking for branch) including error handling 
    if Cas in ["OC","SC","ST","BC_A","BC_B","BC_C","BC_D","BC_E"]:
        branches_list = ''
        for row in range(len(branches_df)):
            short_form = branches_df['Branch_Code'][row]
            full_form = branches_df['Branch_Name'][row]
            #full_form = full_form.replace(")", "")x
            branches_list += "{0:5}\t -- {1}\n".format(short_form, full_form)
        print(branches_list)
        bot.send_message(user_id,branches_list)
        bot.send_message(user_id, " Now, please enter your interested BRANCH CODE i.e short form of the course name from the above list:")
        bot.register_next_step_handler(message, lambda msg: branch(msg,Gen,Cas))
    else:
        bot.send_message(user_id,"Invalid caste please enter valid caste as in mentioned above format")
        # if caste is invalid again asking for the caste from user
        bot.register_next_step_handler(message, lambda msg: caste(msg, Gen))

# Handle user input for branch
def branch(message,Gen,Cas):
    
    user_id = message.from_user.id
    dept = message.text.strip().upper()
    # continuing to next step (asking EAPCET rank) including error handling

    bot.send_message(user_id, "Excellent! Now, please enter your accurate EAPCET rank:")
    print(Gen,Cas,dept)
    bot.register_next_step_handler(message, lambda msg: rank(msg,Gen,Cas,dept))
    

# Handle user input for rank
def rank(message,Gen,Cas,dept):
    user_id = message.from_user.id
    
    user_rank = message.text.strip()
    try:
        user_rank = float(user_rank)
    

        print([Gen,Cas,dept,user_rank])
    
    
        # Recommendation logic here
    
        filtered_data = recommend_colleges(user_rank, dept, Cas)
        recommendations = generate_recommendations(filtered_data)
        #demo = 'College'+'--' +'Rank'
        # Send recommendations to the user
        #bot.send_message(message.chat.id, "Recommended Colleges:")
        # for i in recommendations:
            # print(i)
        bot.send_message(message.chat.id, recommendations)
        bot.send_message(admin_user_id,message.chat.first_name+' got this message \n'+recommendations)
        print(recommendations)

    except ValueError:
        
        bot.send_message(user_id, "Invalid input. Please enter a valid numeric rank ")
        bot.register_next_step_handler(message, lambda msg: rank(msg, Gen, Cas, dept))




@bot.message_handler(commands=['help'])
def help_message(message):
    help_text = "Welcome to the Online Prices Monitor Bot!\n\n"
    help_text += "This bot helps you to recommend colleges based on the rank,caste and selected branch by user.\n\n"
    help_text += "Here are the available commands:\n\n"
    help_text += "/start - Start the bot and get a welcome message.\n"
    help_text += "/help - for any help email to saranyaammu456@gmail.com  \n"
    help_text += "Enjoy EAPCET Counselling  bot and get appropriate college recommendations! 😊"
    bot.send_message(message.chat.id, help_text)


    #bot.send_message(message.chat.id, "THANK YOUUUU :))")

# Step 4: Rank, Branch, and Caste-Based-Gender Filtering
def recommend_colleges(user_rank, user_branch, user_caste,  rank_range=1000):
    filtered_data = data_2023[
        (data_2023['Rank'] >= user_rank - rank_range) &
        (data_2023['Rank'] <= user_rank + rank_range) &
        (data_2023['Branch'] == user_branch) &
        (data_2023['Caste'] == user_caste) 
        
    ]
    return filtered_data

# Step 5: Recommendation Generation
def generate_recommendations(filtered_data, top_n=10):
    # Group the filtered data by college and find the maximum rank for each college
    college_ranks = filtered_data.groupby('College')['Rank'].max().reset_index()
    if len(college_ranks)==0:
        return "It seems like no colleges matched to your criteria !!!"
    
    else:
        # Sort the colleges based on the maximum rank and select the top n colleges
        #top_colleges = college_ranks.sort_values(by='Rank').head(top_n)

        sorted_colleges = college_ranks.sort_values(by='Rank')

        # Create a formatted string with college and rank information
        recommendations_str = "RECOMMENDED COLLEGES ARE :\n\n"   
        for idx, row in sorted_colleges.iterrows():
            college = row['College']
            rank = row['Rank']
            recommendations_str += f"{college}(Rank: {rank})\n\n"
        print(recommendations_str)
        return recommendations_str


def start_polling():
    while True:
        try:
            bot.polling(none_stop=True, interval=1)
        except Exception as e:
            bot.send_message(admin_user_id,f"An error occurred during polling: {e}")
            print(f"An error occurred during polling: {e}")
            time.sleep(3)
        print("Restarting the bot...")
        bot.send_message(admin_user_id,"Restarting the bot...")

polling_thread = threading.Thread(target=start_polling)
polling_thread.daemon = True
polling_thread.start()

'''while True:
    time.sleep(1)'''


if __name__ == '__main__':
    # The following line is no longer needed since polling is handled in the separate thread
    # bot.polling()
    
    # Keep the main program running
    while True:
        time.sleep(1)
