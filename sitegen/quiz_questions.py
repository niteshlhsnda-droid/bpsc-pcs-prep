#!/usr/bin/env python3
"""Original Bihar GK multiple-choice questions for the interactive quiz page.

All facts are drawn from this repo's own verified rapid-fire notes. Written
fresh for the site — no copied question banks.
Each entry: q (question), opts (4 options), a (index of correct option),
why (one-line explanation shown after answering).
"""

QUESTIONS = [
    {
        "q": "The Ganga enters Bihar at which place?",
        "opts": ["Chausa (Buxar)", "Hajipur", "Munger", "Katihar"],
        "a": 0,
        "why": "The Ganga enters Bihar at Chausa in Buxar district and exits at Katihar, bisecting the state west to east.",
    },
    {
        "q": "Which river is called the \u201cSorrow of Bihar\u201d?",
        "opts": ["Son", "Kosi", "Gandak", "Punpun"],
        "a": 1,
        "why": "The Kosi is called the Sorrow of Bihar for its history of shifting course and devastating floods.",
    },
    {
        "q": "How many districts does Bihar have?",
        "opts": ["28", "33", "38", "45"],
        "a": 2,
        "why": "Bihar has 38 districts grouped into 9 divisions.",
    },
    {
        "q": "How many seats are there in the Bihar Vidhan Sabha?",
        "opts": ["243", "233", "250", "225"],
        "a": 0,
        "why": "The Bihar Legislative Assembly has 243 seats; the Vidhan Parishad has 75.",
    },
    {
        "q": "Dr. Rajendra Prasad, India's first President, was born in which Bihar village?",
        "opts": ["Sasaram", "Ziradei (Siwan)", "Vaishali", "Rajgir"],
        "a": 1,
        "why": "Dr. Rajendra Prasad was born at Ziradei in Siwan district, Bihar.",
    },
    {
        "q": "Nalanda University was founded during the reign of which ruler?",
        "opts": ["Ashoka", "Kumaragupta I", "Harshavardhana", "Dharmapala"],
        "a": 1,
        "why": "Nalanda was founded under the Gupta ruler Kumaragupta I; Vikramshila came later under the Pala king Dharmapala.",
    },
    {
        "q": "Vikramshila University was established by which Pala king?",
        "opts": ["Gopala", "Devapala", "Dharmapala", "Mahipala"],
        "a": 2,
        "why": "The Pala king Dharmapala founded Vikramshila in present-day Bhagalpur region.",
    },
    {
        "q": "Mahavira, the 24th Tirthankara, was born at which place in Bihar?",
        "opts": ["Bodh Gaya", "Rajgir", "Vaishali (Kundagrama)", "Pawapuri"],
        "a": 2,
        "why": "Mahavira was born at Kundagrama near Vaishali; he attained nirvana at Pawapuri.",
    },
    {
        "q": "The Buddha attained enlightenment at which site in Bihar?",
        "opts": ["Rajgir", "Vaishali", "Bodh Gaya", "Nalanda"],
        "a": 2,
        "why": "The Buddha attained enlightenment at Bodh Gaya under the Bodhi tree.",
    },
    {
        "q": "The first Buddhist council was held at which place?",
        "opts": ["Vaishali", "Rajgir", "Pataliputra", "Sarnath"],
        "a": 1,
        "why": "The first Buddhist council met at Rajgir; the second was held at Vaishali.",
    },
    {
        "q": "Sher Shah Suri, who built the Grand Trunk Road and introduced the rupiya, belonged to which Bihar town?",
        "opts": ["Arrah", "Sasaram", "Gaya", "Darbhanga"],
        "a": 1,
        "why": "Sher Shah Suri was from Sasaram; his tomb there is a landmark of Indo-Islamic architecture.",
    },
    {
        "q": "The Battle of Buxar, which gave the East India Company the Diwani of Bengal, was fought in which year?",
        "opts": ["1757", "1764", "1772", "1782"],
        "a": 1,
        "why": "Buxar (1764) was the decisive battle; the Diwani of Bengal followed in 1765.",
    },
    {
        "q": "Gandhi's first satyagraha in India, against the tinkathia system, was launched at which place in 1917?",
        "opts": ["Kheda", "Champaran", "Ahmedabad", "Bardoli"],
        "a": 1,
        "why": "The Champaran Satyagraha (1917) in Bihar was Gandhi's first satyagraha in India.",
    },
    {
        "q": "Kunwar Singh, who led the 1857 revolt in Bihar past the age of 80, belonged to which place?",
        "opts": ["Jagdishpur (Arrah)", "Siwan", "Chapra", "Motihari"],
        "a": 0,
        "why": "The octogenarian Kunwar Singh of Jagdishpur near Arrah led Bihar's 1857 uprising.",
    },
    {
        "q": "Bihar Diwas is celebrated on which date?",
        "opts": ["15 November", "22 March", "26 January", "14 April"],
        "a": 1,
        "why": "Bihar Diwas is 22 March, marking the 1912 carving of Bihar & Orissa out of Bengal.",
    },
    {
        "q": "Jharkhand was carved out of Bihar on which date?",
        "opts": ["15 August 1947", "26 January 1950", "15 November 2000", "1 April 1936"],
        "a": 2,
        "why": "Jharkhand was formed on 15 November 2000, bifurcating Bihar.",
    },
    {
        "q": "The Patna High Court was established in which year?",
        "opts": ["1905", "1916", "1936", "1950"],
        "a": 1,
        "why": "The Patna High Court was established in 1916, one of India's oldest high courts.",
    },
    {
        "q": "Who was the first Chief Minister of Bihar?",
        "opts": ["Jairamdas Daulatram", "Sri Krishna Sinha", "Anugrah Narayan Sinha", "Karpuri Thakur"],
        "a": 1,
        "why": "Sri Krishna Sinha became Bihar's first Chief Minister; Jairamdas Daulatram was the first Governor.",
    },
    {
        "q": "Chhath, Bihar's defining festival, is dedicated to which deity?",
        "opts": ["Vishnu", "Shiva", "Sun god (Surya)", "Goddess Durga"],
        "a": 2,
        "why": "Chhath is dedicated to Surya, the Sun god, observed in the month of Kartik.",
    },
    {
        "q": "The Sonepur Mela, among Asia's largest cattle fairs, is held at the confluence of which rivers?",
        "opts": ["Ganga and Son", "Ganga and Gandak", "Ganga and Kosi", "Son and Punpun"],
        "a": 1,
        "why": "Sonepur Mela (Saran) is held at the Ganga\u2013Gandak confluence near Hajipur.",
    },
    {
        "q": "Which traditional Bihar craft holds a GI tag and is painted by Maithil women?",
        "opts": ["Sujini embroidery", "Madhubani/Mithila painting", "Tikuli art", "Khatwa applique"],
        "a": 1,
        "why": "Madhubani (Mithila) painting holds a GI tag; Sikki grass work is another GI-tagged Bihar craft.",
    },
    {
        "q": "Bihar is India's largest producer of which of the following?",
        "opts": ["Makhana (fox nut)", "Almonds", "Cashew", "Walnuts"],
        "a": 0,
        "why": "Bihar's Mithila region is India's #1 makhana producer; makhana holds a GI tag.",
    },
    {
        "q": "The Muzaffarpur belt of Bihar is famous as India's top producer of which fruit?",
        "opts": ["Mango", "Banana", "Litchi", "Guava"],
        "a": 2,
        "why": "Bihar is India's #1 litchi producer, centred on the Muzaffarpur belt.",
    },
    {
        "q": "Which of these is a north-bank, Himalayan-origin river of Bihar?",
        "opts": ["Son", "Punpun", "Gandak", "Falgu"],
        "a": 2,
        "why": "North-bank Himalayan rivers \u2014 Gandak, Burhi Gandak, Bagmati, Kosi, Mahananda \u2014 are flood-prone; Son, Punpun and Falgu are seasonal south-bank rivers.",
    },
]
