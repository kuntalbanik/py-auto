# Rock, Paper & Scissiors game
# ---
# খেলার নিয়ম (Core Rules)
# খেলাটিতে ৩টি উপাদান থাকে এবং প্রত্যেকের একটি নির্দিষ্ট ক্ষমতা থাকে:
# Rock (পাথর): Scissors (কাঁচি)-কে ভেঙে ফেলে। (Rock wins against Scissors)
# Scissors (কাঁচি): Paper (কাগজ)-কে কেটে ফেলে। (Scissors wins against Paper)
# Paper (কাগজ): Rock (পাথর)-কে মুড়িয়ে ফেলে। (Paper wins against Rock)
# যদি দুইজন খেলোয়াড় একই উপাদান বেছে নেয় (যেমন: দুইজনই Rock দিল), তবে ম্যাচটি
# Tie # (ড্র) হয়।
# ---

import random
input_text = '''
Rock, Paper & Scissiors game
Choose - Rock : 0, Paper: 1, Scissor: 2 \n
'''
user_choice = int(input(input_text))

computer_choice = random.randint(0, 2)
print("Computer choice : ", computer_choice)
if user_choice == computer_choice:
    print("It's a Draw")
elif computer_choice == 2 and user_choice == 1:
    print("Computer win!")
elif computer_choice == 1 and user_choice == 0:
    print("Computer win!")
elif computer_choice == 0 and user_choice == 2:
    print("Computer win!")
else:
    print("You Win!")
