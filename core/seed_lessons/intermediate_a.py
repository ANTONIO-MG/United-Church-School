"""Intermediate Phase (part A): Term 1, Week 1 demo lessons.

Offerings (9): Grades 4, 5 and 6 x
    ENG-HL   English Home Language
    ZUL-FAL  isiZulu First Additional Language
    MATH     Mathematics

CAPS sources used
    * CAPS Mathematics Intermediate Phase Gr 4-6 (DBE) and the 2026 / recovery Annual
      Teaching Plans, Term 1 week 1: Whole numbers - counting, ordering, comparing,
      representing and place value (Gr 4: at least 4-digit numbers, to 10 000;
      Gr 5: at least 6-digit numbers; Gr 6: at least 9-digit numbers), rounding off.
    * CAPS English Home Language Intermediate Phase Gr 4-6 and Term 1 ATP, two-week
      cycle 1: Listening & Speaking (listening comprehension of a story / folktale),
      Reading & Viewing (reading comprehension, story elements), Writing (paragraph /
      narrative), Language Structures & Conventions (nouns, verbs, punctuation).
    * CAPS isiZulu First Additional Language Intermediate Phase Gr 4-6 and Term 1 ATP,
      cycle 1: Ukulalela nokukhuluma (listening & speaking) - ukubingelela (greetings),
      ukuzethula (introducing yourself), umndeni (family), classroom language and
      simple dialogues.

The stories in the English lessons are original retellings written for these lessons.
"""

LESSONS = {
    # =====================================================================
    # GRADE 4 MATHEMATICS
    # =====================================================================
    (4, 'MATH'): {
        'topic': 'Whole numbers: counting, place value, comparing and ordering to 10 000',
        'caps': 'CAPS Mathematics Gr 4 Term 1 (ATP week 1): Numbers, Operations and Relationships - '
                'whole numbers: count forwards and backwards; order, compare and represent numbers '
                'to at least 4-digit numbers (0 to 10 000); recognise the place value of digits',
        'summary': 'Learners read, write and count with numbers up to 10 000, find the value of each '
                   'digit using expanded notation, and compare and order 4-digit numbers.',
        'days': [
            {
                'title': 'Counting, reading and writing numbers to 10 000',
                'minutes': 45,
                'objectives': [
                    'I can read and write 4-digit numbers in numerals and in words.',
                    'I can count forwards and backwards in 10s, 25s, 50s, 100s and 1 000s.',
                    'I can say which number comes just before or just after a given number.',
                ],
                'notes': (
                    '<p>Welcome to Grade 4 Mathematics! This year we work with <strong>bigger numbers</strong>, '
                    'up to <strong>10 000</strong> (ten thousand).</p>'
                    '<p>A 4-digit number such as <strong>4 563</strong> has four places: '
                    '<strong>thousands</strong>, <strong>hundreds</strong>, <strong>tens</strong> and '
                    '<strong>units</strong> (ones). In South Africa we leave a small <em>space</em> between the '
                    'thousands and the hundreds: we write 4 563, not 4563.</p>'
                    '<p><strong>Reading and writing numbers in words</strong></p>'
                    '<ul><li>4 563 is <em>four thousand five hundred and sixty-three</em>.</li>'
                    '<li>2 017 is <em>two thousand and seventeen</em> (there are no hundreds, so we say nothing for them).</li>'
                    '<li>9 300 is <em>nine thousand three hundred</em>.</li></ul>'
                    '<p><strong>Counting</strong></p>'
                    '<p>When we count in 100s, only the hundreds digit changes, until we pass 9 hundreds: '
                    '3 850, 3 950, <strong>4 050</strong>. Ten hundreds make one thousand, so the thousands digit goes up by 1.</p>'
                    '<p>When we count backwards in 1 000s, the thousands digit goes down by 1 each time: '
                    '9 315, 8 315, 7 315 ...</p>'
                    '<p>The number <strong>just after</strong> 4 999 is 5 000. The number <strong>just before</strong> 7 000 is 6 999.</p>'
                ),
                'key_terms': [
                    ('digit', 'One of the symbols 0, 1, 2, 3, 4, 5, 6, 7, 8, 9 that we use to write numbers.'),
                    ('numeral', 'A number written with digits, e.g. 4 563.'),
                    ('thousand', '10 hundreds, written 1 000.'),
                    ('count backwards', 'Count down, making the number smaller each time.'),
                ],
                'example': {
                    'title': 'Worked example: reading, writing and counting',
                    'html': (
                        '<p><strong>1. Write 7 208 in words.</strong></p>'
                        '<p>7 thousands, 2 hundreds, 0 tens, 8 units: <em>seven thousand two hundred and eight</em>. '
                        'The 0 tells us there are no tens.</p>'
                        '<p><strong>2. Write "six thousand and forty-two" in numerals.</strong></p>'
                        '<p>6 thousands, 0 hundreds, 4 tens, 2 units: <strong>6 042</strong>.</p>'
                        '<p><strong>3. Count forwards in 25s from 1 150.</strong></p>'
                        '<p>1 150, 1 175, 1 200, 1 225, 1 250 (every four jumps of 25 make 100).</p>'
                    ),
                },
                'video': {'id': '1jVWFJWHtIU', 'title': 'Place Value in 4 Digit Numbers | KS2 Maths Year 3 & 4',
                          'channel': 'CENTURY Tech', 'minutes': 5},
                'worksheet': {
                    'instructions': 'Answer all the questions. Remember to leave a space between the thousands and the hundreds.',
                    'exercises': [
                        '1. Write 3 645 in words.',
                        '2. Write "six thousand and forty-two" in numerals.',
                        '3. Write "nine thousand nine hundred and nine" in numerals.',
                        '4. Count forwards in 100s: 2 760; 2 860; ____; ____; ____',
                        '5. Count backwards in 1 000s: 9 315; 8 315; ____; ____; ____',
                        '6. Count forwards in 50s: 4 850; 4 900; ____; ____; ____',
                        '7. Which number comes just after 4 999? Which number comes just before 7 000?',
                    ],
                },
                'quiz': [
                    ('mcq', 'How do we write "five thousand and seventy" in numerals?',
                     ['5 700', '5 070', '5 007', '50 070'], 1),
                    ('tf', 'Counting forwards in 100s from 3 950, the next number is 4 050.', True),
                    ('mcq', 'Which number comes just before 8 000?', ['7 900', '8 001', '7 999', '7 000'], 2),
                    ('mcq', 'Count in 50s: 2 400; 2 450; 2 500; ... What comes next?',
                     ['2 550', '2 600', '2 505', '3 000'], 0),
                ],
                'homework': {
                    'title': 'Big numbers at home',
                    'instructions': 'Look for numbers bigger than 1 000 at home and practise counting.',
                    'tasks': [
                        'Find 3 numbers bigger than 1 000 at home (on a calendar, a price tag or a box). Write each one in numerals and in words.',
                        'Count backwards in 10s from 5 030 to 4 940. Write every number.',
                    ],
                    'marks': 10,
                },
            },
            {
                'title': 'Place value, value of digits and expanded notation',
                'minutes': 45,
                'objectives': [
                    'I can name the place of each digit in a 4-digit number.',
                    'I can give the value of a digit, e.g. the 3 in 6 384 is worth 300.',
                    'I can write a number in expanded notation and build it again.',
                ],
                'notes': (
                    '<p>Every digit in a number has a <strong>place</strong> and a <strong>value</strong>. '
                    'The place tells us how much the digit is worth.</p>'
                    '<p>Look at <strong>6 384</strong>:</p>'
                    '<ul><li>6 is in the <strong>thousands</strong> place, so its value is 6 000</li>'
                    '<li>3 is in the <strong>hundreds</strong> place, so its value is 300</li>'
                    '<li>8 is in the <strong>tens</strong> place, so its value is 80</li>'
                    '<li>4 is in the <strong>units</strong> place, so its value is 4</li></ul>'
                    '<p>When we write a number as the sum of the values of its digits, we use '
                    '<strong>expanded notation</strong>: 6 384 = 6 000 + 300 + 80 + 4.</p>'
                    '<p><strong>Zero is a place holder.</strong> In 5 017 there are no hundreds, so we write 0 in the '
                    'hundreds place. In expanded notation we leave the zero out: 5 017 = 5 000 + 10 + 7. '
                    'Without the zero, 5 017 would become 517, a much smaller number!</p>'
                    '<p>Each place is <strong>10 times</strong> bigger than the place to its right: '
                    '10 units = 1 ten, 10 tens = 1 hundred, 10 hundreds = 1 thousand, 10 thousands = 10 000.</p>'
                ),
                'key_terms': [
                    ('place value', 'The value a digit has because of its position in a number.'),
                    ('expanded notation', 'Writing a number as the sum of the values of its digits, e.g. 3 052 = 3 000 + 50 + 2.'),
                    ('place holder', 'A zero that keeps the other digits in their correct places.'),
                ],
                'example': {
                    'title': 'Worked example: breaking up and building numbers',
                    'html': (
                        '<p><strong>Break up 9 406.</strong></p>'
                        '<ul><li>Thousands: 9, value 9 000</li><li>Hundreds: 4, value 400</li>'
                        '<li>Tens: 0, value 0</li><li>Units: 6, value 6</li></ul>'
                        '<p>Expanded notation: 9 406 = 9 000 + 400 + 6</p>'
                        '<p><strong>Build the number 3 000 + 50 + 2.</strong></p>'
                        '<p>3 thousands, 0 hundreds, 5 tens, 2 units: <strong>3 052</strong>.</p>'
                        '<p><strong>Make the biggest number with 3, 9, 1, 6.</strong> Put the biggest digit in the '
                        'thousands place, then the next biggest: <strong>9 631</strong>.</p>'
                    ),
                },
                'video': {'id': 'GjGoqqGYRjo', 'title': 'Expanded Notation of A Number | Mathematics Grade 4 | Periwinkle',
                          'channel': 'Periwinkle', 'minutes': 5},
                'worksheet': {
                    'instructions': 'Answer all the questions. Draw a place value table (Th | H | T | U) if it helps you.',
                    'exercises': [
                        '1. What is the value of the digit 7 in 4 718?',
                        '2. What is the value of the digit 5 in 5 239?',
                        '3. Write 2 847 in expanded notation.',
                        '4. Write 6 090 in expanded notation.',
                        '5. Write as one number: 8 000 + 600 + 4',
                        '6. Write as one number: 1 000 + 900 + 90 + 9',
                        '7. Which digit is in the hundreds place in 7 538?',
                        '8. Make the biggest 4-digit number you can with the digits 3, 9, 1 and 6.',
                    ],
                },
                'quiz': [
                    ('mcq', 'What is the value of the digit 4 in 3 485?', ['4', '40', '400', '4 000'], 2),
                    ('mcq', 'Which number is 7 000 + 30 + 5?', ['7 305', '7 035', '7 350', '73 005'], 1),
                    ('tf', 'In the number 2 609, the 0 is in the tens place.', True),
                    ('mcq', 'Which digit is in the thousands place in 5 812?', ['8', '2', '1', '5'], 3),
                ],
                'homework': {
                    'title': 'Expanded notation practice',
                    'instructions': 'Show all your working in your homework book.',
                    'tasks': [
                        'Write 4 768, 3 205 and 9 050 in expanded notation.',
                        'Use the digits 2, 7, 0 and 5 to make the biggest and the smallest 4-digit numbers. (A number cannot start with 0.)',
                        'Explain to someone at home what the 0 does in 3 205.',
                    ],
                    'marks': 10,
                },
            },
            {
                'title': 'Comparing and ordering numbers to 10 000',
                'minutes': 45,
                'objectives': [
                    'I can compare two 4-digit numbers using >, < and =.',
                    'I can order numbers from smallest to biggest and from biggest to smallest.',
                    'I can place numbers on a number line.',
                ],
                'notes': (
                    '<p>To <strong>compare</strong> two numbers, we decide which one is bigger.</p>'
                    '<ol><li>First count the digits. A 4-digit number is always bigger than a 3-digit number: 1 000 &gt; 999.</li>'
                    '<li>If they have the same number of digits, compare the digits from the <strong>left</strong>, '
                    'starting with the biggest place (the thousands).</li>'
                    '<li>If those digits are the same, move one place to the right and compare again.</li></ol>'
                    '<p>We use these symbols:</p>'
                    '<ul><li><strong>&gt;</strong> means "is greater than": 6 271 &gt; 6 217</li>'
                    '<li><strong>&lt;</strong> means "is less than": 8 090 &lt; 8 900</li>'
                    '<li><strong>=</strong> means "is equal to"</li></ul>'
                    '<p>Tip: the open side of the symbol always faces the <em>bigger</em> number.</p>'
                    '<p>To <strong>order</strong> numbers, we compare them all. <strong>Ascending order</strong> goes from '
                    'the smallest to the biggest. <strong>Descending order</strong> goes from the biggest to the smallest.</p>'
                    '<p>On a <strong>number line</strong> numbers get bigger as we move to the right. '
                    'Halfway between 3 000 and 4 000 is 3 500.</p>'
                ),
                'key_terms': [
                    ('greater than (>)', 'Bigger than.'),
                    ('less than (<)', 'Smaller than.'),
                    ('ascending order', 'From the smallest to the biggest.'),
                    ('descending order', 'From the biggest to the smallest.'),
                ],
                'example': {
                    'title': 'Worked example: compare and order',
                    'html': (
                        '<p><strong>Compare 4 582 and 4 528.</strong></p>'
                        '<p>Thousands: 4 and 4 (same). Hundreds: 5 and 5 (same). Tens: 8 and 2. 8 is bigger, so '
                        '<strong>4 582 &gt; 4 528</strong>.</p>'
                        '<p><strong>Put in ascending order: 3 409; 3 940; 3 094; 4 039</strong></p>'
                        '<p>4 039 has the most thousands, so it is the biggest. The other three all have 3 thousands, '
                        'so compare the hundreds: 0, 4, 9.</p>'
                        '<p>Answer: 3 094; 3 409; 3 940; 4 039</p>'
                    ),
                },
                'video': {'id': 'TOrcUx0wDDQ', 'title': 'Comparing Whole Numbers - Math Antics Extras',
                          'channel': 'mathantics', 'minutes': 5},
                'worksheet': {
                    'instructions': 'Fill in <, > or = and answer the questions.',
                    'exercises': [
                        '1. 6 217 ____ 6 271',
                        '2. 8 900 ____ 8 090',
                        '3. 5 000 ____ 4 999',
                        '4. Write in ascending order: 2 518; 2 158; 2 851; 2 815',
                        '5. Write in descending order: 7 060; 7 600; 7 006; 6 700',
                        '6. Which number is halfway between 3 000 and 4 000 on a number line?',
                        '7. Write a number between 5 490 and 5 510 that ends in 0.',
                    ],
                },
                'quiz': [
                    ('mcq', 'Which number is the greatest?', ['6 899', '6 889', '6 998', '6 989'], 2),
                    ('tf', '4 305 < 4 053', False),
                    ('mcq', 'Which list is in ascending order?',
                     ['1 250; 1 205; 1 520', '1 205; 1 250; 1 520', '1 520; 1 250; 1 205', '1 250; 1 520; 1 205'], 1),
                    ('mcq', 'Which symbol makes this true? 9 010 ____ 9 100', ['>', '=', '<'], 2),
                ],
                'homework': {
                    'title': 'Compare and order',
                    'instructions': 'Complete these in your homework book.',
                    'tasks': [
                        'Write in ascending order: 4 210; 4 021; 4 201; 4 012',
                        'Fill in < or >: (a) 3 333 ____ 3 303   (b) 8 040 ____ 8 400',
                        'Draw a number line from 2 000 to 3 000, mark every 100, and show where 2 450 is.',
                    ],
                    'marks': 10,
                },
            },
        ],
    },

    # =====================================================================
    # GRADE 5 MATHEMATICS
    # =====================================================================
    (5, 'MATH'): {
        'topic': 'Whole numbers: counting, place value, comparing, ordering and rounding (6-digit numbers)',
        'caps': 'CAPS Mathematics Gr 5 Term 1 (ATP week 1): Numbers, Operations and Relationships - '
                'whole numbers: count, order, compare and represent numbers to at least 6-digit numbers; '
                'recognise the place value of digits; round off to the nearest 5, 10, 100 and 1 000',
        'summary': 'Learners read and write 6-digit numbers, use place value and expanded notation, '
                   'and compare, order and round off whole numbers.',
        'days': [
            {
                'title': 'Reading, writing and counting with 6-digit numbers',
                'minutes': 50,
                'objectives': [
                    'I can read and write 6-digit numbers in numerals and in words.',
                    'I can count forwards and backwards in 1 000s, 10 000s and 100 000s.',
                    'I can explain how digits are grouped in threes.',
                ],
                'notes': (
                    '<p>In Grade 5 we work with numbers up to at least <strong>six digits</strong>, '
                    'for example <strong>345 210</strong>. The biggest 6-digit number is 999 999, and '
                    'one more is <strong>1 000 000</strong> (one million).</p>'
                    '<p>We group digits in threes from the right and leave a space between groups:</p>'
                    '<ul><li>The <strong>units group</strong>: hundreds, tens, units</li>'
                    '<li>The <strong>thousands group</strong>: hundred thousands, ten thousands, thousands</li></ul>'
                    '<p>To read a big number, read each group and then say its name. '
                    '345 210 is <em>three hundred and forty-five <strong>thousand</strong>, two hundred and ten</em>.</p>'
                    '<p>Be careful with zeros: 608 075 is <em>six hundred and eight thousand and seventy-five</em>. '
                    'There are no hundreds, so we say nothing for them.</p>'
                    '<p><strong>Counting</strong>: when we count in 1 000s, the thousands digit changes; when it '
                    'passes 9, we regroup into the ten thousands. 98 500; 99 500; <strong>100 500</strong>. '
                    'Counting backwards in 10 000s from 532 000 gives 522 000; 512 000; 502 000; 492 000.</p>'
                ),
                'key_terms': [
                    ('ten thousand', '10 000 = ten thousands.'),
                    ('hundred thousand', '100 000 = ten ten-thousands.'),
                    ('one million', '1 000 000 = one thousand thousands.'),
                ],
                'example': {
                    'title': 'Worked example: words and numerals',
                    'html': (
                        '<p><strong>1. Write 700 406 in words.</strong></p>'
                        '<p>Thousands group: 700, so "seven hundred thousand". Units group: 406, so "four hundred and six".</p>'
                        '<p>Answer: <em>seven hundred thousand, four hundred and six</em>.</p>'
                        '<p><strong>2. Write "ninety thousand and fifty" in numerals.</strong></p>'
                        '<p>Thousands group: 90. Units group: 050. Answer: <strong>90 050</strong>.</p>'
                        '<p><strong>3. Count forwards in 1 000s from 497 500.</strong></p>'
                        '<p>498 500; 499 500; 500 500; 501 500</p>'
                    ),
                },
                'video': {'id': 'lDXUtDhgFc0', 'title': 'Learn Place Value up to 1 Million Fast!',
                          'channel': 'Maths with Mrs B.', 'minutes': 4},
                'worksheet': {
                    'instructions': 'Answer all the questions. Group digits in threes with a space between groups.',
                    'exercises': [
                        '1. Write 254 318 in words.',
                        '2. Write 700 406 in words.',
                        '3. Write in numerals: four hundred and twelve thousand, nine hundred and three.',
                        '4. Write in numerals: ninety thousand and fifty.',
                        '5. Count forwards in 1 000s: 186 700; 187 700; ____; ____; ____',
                        '6. Count backwards in 10 000s: 532 000; 522 000; ____; ____; ____',
                        '7. What is 1 more than 399 999? What is 1 less than 600 000?',
                    ],
                },
                'quiz': [
                    ('mcq', 'How do we write "three hundred and six thousand and forty"?',
                     ['306 400', '360 040', '306 040', '30 640'], 2),
                    ('tf', 'The number after 299 999 is 300 000.', True),
                    ('mcq', 'Count in 1 000s: 98 500; 99 500; ... What comes next?',
                     ['100 500', '99 600', '100 000', '109 500'], 0),
                    ('mcq', 'How many digits does 100 000 have?', ['5', '6', '7'], 1),
                ],
                'homework': {
                    'title': 'Six-digit numbers',
                    'instructions': 'Write neatly and group the digits in threes.',
                    'tasks': [
                        'Make up three 6-digit numbers of your own. Write each one in numerals and in words.',
                        'Count forwards in 25 000s from 25 000 to 250 000.',
                        'Write the number that is 10 000 more than 495 300.',
                    ],
                    'marks': 12,
                },
            },
            {
                'title': 'Place value and expanded notation to 6 digits',
                'minutes': 50,
                'objectives': [
                    'I can give the place and value of any digit in a 6-digit number.',
                    'I can write 6-digit numbers in expanded notation.',
                    'I can explain that each place is 10 times the place to its right.',
                ],
                'notes': (
                    '<p>Look at the number <strong>472 615</strong> in a place value table:</p>'
                    '<ul><li>4 hundred thousands: value 400 000</li>'
                    '<li>7 ten thousands: value 70 000</li>'
                    '<li>2 thousands: value 2 000</li>'
                    '<li>6 hundreds: value 600</li>'
                    '<li>1 ten: value 10</li>'
                    '<li>5 units: value 5</li></ul>'
                    '<p><strong>Expanded notation</strong>: 472 615 = 400 000 + 70 000 + 2 000 + 600 + 10 + 5</p>'
                    '<p>The <strong>place</strong> of a digit is its position (e.g. ten thousands). The '
                    '<strong>value</strong> is what it is worth there (e.g. 70 000). The same digit can have '
                    'different values: in 44 000 the first 4 is worth 40 000 and the second 4 is worth 4 000. '
                    'The first one is <strong>10 times</strong> bigger, because every place is ten times the place to its right.</p>'
                    '<p>Zeros are <strong>place holders</strong>. 607 020 = 600 000 + 7 000 + 20. We leave out the zero '
                    'places when we expand, but we must write the zeros when we build the number again.</p>'
                ),
                'key_terms': [
                    ('place', 'The position of a digit in a number, e.g. hundred thousands.'),
                    ('value', 'What a digit is worth in its place, e.g. the 7 in 472 615 is worth 70 000.'),
                    ('expanded notation', 'A number written as the sum of the values of its digits.'),
                ],
                'example': {
                    'title': 'Worked example: expanding and building',
                    'html': (
                        '<p><strong>1. Write 803 260 in expanded notation.</strong></p>'
                        '<p>8 hundred thousands, 0 ten thousands, 3 thousands, 2 hundreds, 6 tens, 0 units.</p>'
                        '<p>803 260 = 800 000 + 3 000 + 200 + 60</p>'
                        '<p><strong>2. Write 500 000 + 40 000 + 300 + 9 as one number.</strong></p>'
                        '<p>Fill each place: 5 | 4 | 0 | 3 | 0 | 9, so the number is <strong>540 309</strong>.</p>'
                        '<p><strong>3. Make the smallest 6-digit number with 0, 3, 5, 8, 1, 9.</strong></p>'
                        '<p>It cannot start with 0, so start with 1, then put the 0, then the rest from smallest: <strong>103 589</strong>.</p>'
                    ),
                },
                'video': {'id': 'T5Qf0qSSJFI', 'title': 'Math Antics - Place Value', 'channel': 'mathantics', 'minutes': 9},
                'worksheet': {
                    'instructions': 'Answer all the questions. Use a place value table if it helps.',
                    'exercises': [
                        '1. What is the value of the digit 8 in 584 302?',
                        '2. What is the value of the digit 6 in 213 657?',
                        '3. Write 359 784 in expanded notation.',
                        '4. Write 607 020 in expanded notation.',
                        '5. Write as one number: 500 000 + 40 000 + 300 + 9',
                        '6. Which digit is in the ten thousands place in 728 145?',
                        '7. In 44 000, how many times bigger is the value of the first 4 than the second 4?',
                        '8. Make the smallest 6-digit number using 0, 3, 5, 8, 1 and 9.',
                    ],
                },
                'quiz': [
                    ('mcq', 'What is the value of the 5 in 452 107?', ['5 000', '50 000', '500', '500 000'], 1),
                    ('mcq', 'Which number is 600 000 + 8 000 + 70 + 3?', ['608 073', '680 073', '608 730', '600 873'], 0),
                    ('tf', 'In 315 924, the digit 1 is in the ten thousands place.', True),
                    ('mcq', 'Which digit is in the hundreds place in 270 418?', ['0', '1', '4', '8'], 2),
                ],
                'homework': {
                    'title': 'Place value challenge',
                    'instructions': 'Show your working in your homework book.',
                    'tasks': [
                        'Write 918 437, 250 006 and 703 050 in expanded notation.',
                        'Use the digits 4, 0, 7, 2, 9 and 5 to make the biggest and the smallest 6-digit numbers.',
                        'Write the value of every digit in 386 514.',
                    ],
                    'marks': 12,
                },
            },
            {
                'title': 'Comparing, ordering and rounding off whole numbers',
                'minutes': 50,
                'objectives': [
                    'I can compare and order 6-digit numbers using <, > and =.',
                    'I can round off numbers to the nearest 10, 100 and 1 000.',
                    'I can explain the rounding rule.',
                ],
                'notes': (
                    '<p><strong>Comparing</strong>: count the digits first; more digits means a bigger number. '
                    'If the numbers have the same number of digits, compare place by place from the left. '
                    '405 312 &lt; 450 312 because 0 ten thousands is less than 5 ten thousands.</p>'
                    '<p><strong>Ordering</strong>: ascending = smallest to biggest; descending = biggest to smallest.</p>'
                    '<p><strong>Rounding off</strong> gives a number that is close to the real number but easier to work with. '
                    'Follow these steps:</p>'
                    '<ol><li>Find the digit in the place you are rounding to.</li>'
                    '<li>Look at the digit just to its <strong>right</strong>.</li>'
                    '<li>If that digit is <strong>5 or more</strong>, round <strong>up</strong> (add 1 to your digit). '
                    'If it is <strong>4 or less</strong>, keep your digit.</li>'
                    '<li>Change all the digits to the right into zeros.</li></ol>'
                    '<p>Round 346 782:</p>'
                    '<ul><li>to the nearest 10: look at the units (2), round down: 346 780</li>'
                    '<li>to the nearest 100: look at the tens (8), round up: 346 800</li>'
                    '<li>to the nearest 1 000: look at the hundreds (7), round up: 347 000</li></ul>'
                ),
                'key_terms': [
                    ('round off', 'Change a number to the nearest 10, 100, 1 000 ... to make it easier to work with.'),
                    ('ascending', 'From the smallest to the biggest.'),
                    ('descending', 'From the biggest to the smallest.'),
                ],
                'example': {
                    'title': 'Worked example: order and round',
                    'html': (
                        '<p><strong>1. Ascending order: 245 610; 254 160; 245 160; 254 016</strong></p>'
                        '<p>Two numbers start with 245 and two with 254, so the 245s come first. 245 160 &lt; 245 610 '
                        '(compare hundreds: 1 &lt; 6). 254 016 &lt; 254 160 (compare hundreds: 0 &lt; 1).</p>'
                        '<p>Answer: 245 160; 245 610; 254 016; 254 160</p>'
                        '<p><strong>2. Round 128 465.</strong></p>'
                        '<ul><li>Nearest 10: units digit 5, round up: 128 470</li>'
                        '<li>Nearest 100: tens digit 6, round up: 128 500</li>'
                        '<li>Nearest 1 000: hundreds digit 4, round down: 128 000</li></ul>'
                    ),
                },
                'video': {'id': 'XoqYZgBcio0', 'title': 'Rounding Numbers to the Nearest 10, 100, and 1000 | Round up and Round down',
                          'channel': 'Tutoring Hour', 'minutes': 5},
                'worksheet': {
                    'instructions': 'Fill in <, > or =, then order and round the numbers.',
                    'exercises': [
                        '1. 405 312 ____ 450 312',
                        '2. 999 999 ____ 1 000 000',
                        '3. Write in ascending order: 312 450; 321 405; 312 540; 302 451',
                        '4. Write in descending order: 89 999; 98 000; 90 100; 89 990',
                        '5. Round 73 846 to the nearest 10.',
                        '6. Round 73 846 to the nearest 100.',
                        '7. Round 73 846 to the nearest 1 000.',
                    ],
                },
                'quiz': [
                    ('mcq', 'Which number is the smallest?', ['560 089', '506 980', '560 908', '506 089'], 3),
                    ('mcq', 'Round 258 643 to the nearest 1 000.', ['258 000', '259 000', '260 000', '258 600'], 1),
                    ('tf', '634 150 rounded to the nearest 100 is 634 100.', False),
                    ('mcq', 'Which symbol makes this true? 700 070 ____ 700 700', ['<', '>', '='], 0),
                ],
                'homework': {
                    'title': 'Rounding off',
                    'instructions': 'Show which digit you looked at each time.',
                    'tasks': [
                        'Round 47 365 to the nearest 10, 100 and 1 000.',
                        'Round 205 718 to the nearest 10, 100 and 1 000.',
                        'Write in ascending order: 610 016; 601 160; 610 160; 601 016',
                    ],
                    'marks': 15,
                },
            },
        ],
    },

    # =====================================================================
    # GRADE 6 MATHEMATICS
    # =====================================================================
    (6, 'MATH'): {
        'topic': 'Whole numbers: counting, place value, comparing, ordering and rounding (9-digit numbers)',
        'caps': 'CAPS Mathematics Gr 6 Term 1 (ATP week 1): Numbers, Operations and Relationships - '
                'whole numbers: count, order, compare and represent numbers to at least 9-digit numbers; '
                'recognise the place value of digits; round off to the nearest 5, 10, 100 and 1 000',
        'summary': 'Learners read and write numbers up to 9 digits (hundreds of millions), use place value and '
                   'expanded notation, and compare, order and round off whole numbers.',
        'days': [
            {
                'title': 'Reading and writing numbers to 9 digits',
                'minutes': 50,
                'objectives': [
                    'I can read and write numbers up to 9 digits in numerals and in words.',
                    'I can name the three groups: millions, thousands and units.',
                    'I can count forwards and backwards in 100 000s and 1 000 000s.',
                ],
                'notes': (
                    '<p>In Grade 6 we work with numbers up to at least <strong>nine digits</strong>, such as '
                    '<strong>245 309 817</strong>. These numbers are in the <strong>hundreds of millions</strong>.</p>'
                    '<p>Digits are grouped in threes, from the right:</p>'
                    '<ul><li><strong>Millions group</strong>: hundred millions, ten millions, millions</li>'
                    '<li><strong>Thousands group</strong>: hundred thousands, ten thousands, thousands</li>'
                    '<li><strong>Units group</strong>: hundreds, tens, units</li></ul>'
                    '<p>Read each group as a 3-digit number and then say the group name:</p>'
                    '<p>245 309 817 = <em>two hundred and forty-five <strong>million</strong>, three hundred and nine '
                    '<strong>thousand</strong>, eight hundred and seventeen</em>.</p>'
                    '<p>Remember: 1 million = 1 000 000 = <strong>one thousand thousands</strong>. '
                    'One hundred million (100 000 000) has nine digits.</p>'
                    '<p>When a whole group is zero, we do not say it: 90 000 050 is <em>ninety million and fifty</em>.</p>'
                    '<p><strong>Counting</strong>: in 100 000s, 8 700 000; 8 800 000; 8 900 000; <strong>9 000 000</strong> '
                    '(ten hundred thousands make one million).</p>'
                ),
                'key_terms': [
                    ('million', '1 000 000, a thousand thousands.'),
                    ('ten million', '10 000 000.'),
                    ('hundred million', '100 000 000, the smallest 9-digit number.'),
                    ('group (period)', 'A set of three digits: units, thousands or millions.'),
                ],
                'example': {
                    'title': 'Worked example: big numbers in words and numerals',
                    'html': (
                        '<p><strong>1. Write 507 040 300 in words.</strong></p>'
                        '<p>Millions: 507. Thousands: 040. Units: 300.</p>'
                        '<p><em>Five hundred and seven million, forty thousand, three hundred.</em></p>'
                        '<p><strong>2. Write "twelve million, four hundred thousand and nine" in numerals.</strong></p>'
                        '<p>Millions: 12. Thousands: 400. Units: 009. Answer: <strong>12 400 009</strong>.</p>'
                        '<p><strong>3. Count forwards in 1 000 000s from 4 750 000.</strong></p>'
                        '<p>5 750 000; 6 750 000; 7 750 000</p>'
                    ),
                },
                'video': {'id': 'eAprDy56drY', 'title': '6th Grade Math Tutorials: Place Value to Millions',
                          'channel': 'CTCMath', 'minutes': 4},
                'worksheet': {
                    'instructions': 'Answer all the questions. Group the digits in threes.',
                    'exercises': [
                        '1. Write 368 451 207 in words.',
                        '2. Write 90 006 050 in words.',
                        '3. Write in numerals: twelve million, four hundred thousand and nine.',
                        '4. Write in numerals: six hundred million, sixty thousand and six.',
                        '5. Count forwards in 1 000 000s: 4 750 000; 5 750 000; ____; ____; ____',
                        '6. What is 1 more than 99 999 999?',
                        '7. How many thousands are there in one million?',
                    ],
                },
                'quiz': [
                    ('mcq', 'How do we write "forty million, two hundred thousand and fifteen"?',
                     ['40 200 015', '40 020 015', '4 200 015', '402 000 015'], 0),
                    ('tf', 'One million is the same as one thousand thousands.', True),
                    ('mcq', 'How many digits does one hundred million have?', ['8', '9', '10', '7'], 1),
                    ('mcq', 'Count in 100 000s: 8 700 000; 8 800 000; 8 900 000; ... What comes next?',
                     ['8 910 000', '9 900 000', '9 000 000', '10 000 000'], 2),
                ],
                'homework': {
                    'title': 'Millions',
                    'instructions': 'Write neatly and group digits in threes.',
                    'tasks': [
                        'Make up three 9-digit numbers. Write each one in numerals and in words.',
                        'Count backwards in 1 000 000s from 25 000 000 to 15 000 000.',
                        'Write the smallest and the biggest 9-digit numbers.',
                    ],
                    'marks': 12,
                },
            },
            {
                'title': 'Place value and expanded notation to 9 digits',
                'minutes': 50,
                'objectives': [
                    'I can give the place and value of any digit in a 9-digit number.',
                    'I can write 9-digit numbers in expanded notation.',
                    'I can build a number from its expanded notation.',
                ],
                'notes': (
                    '<p>Each digit has a <strong>place</strong> (its position) and a <strong>value</strong> (what it is worth). '
                    'Look at <strong>735 284 916</strong>:</p>'
                    '<ul><li>7 hundred millions: 700 000 000</li>'
                    '<li>3 ten millions: 30 000 000</li>'
                    '<li>5 millions: 5 000 000</li>'
                    '<li>2 hundred thousands: 200 000</li>'
                    '<li>8 ten thousands: 80 000</li>'
                    '<li>4 thousands: 4 000</li>'
                    '<li>9 hundreds, 1 ten, 6 units: 900, 10 and 6</li></ul>'
                    '<p><strong>Expanded notation</strong>: 735 284 916 = 700 000 000 + 30 000 000 + 5 000 000 + 200 000 '
                    '+ 80 000 + 4 000 + 900 + 10 + 6</p>'
                    '<p>Each place is <strong>10 times</strong> the place to its right. In 770 000 000 the first 7 '
                    '(700 000 000) is ten times the second 7 (70 000 000).</p>'
                    '<p>When you build a number from expanded notation, <strong>write zeros</strong> in every empty place. '
                    'A quick check: count the digits. Anything in the hundred millions must give a 9-digit number.</p>'
                ),
                'key_terms': [
                    ('place value', 'The value of a digit because of its position.'),
                    ('expanded notation', 'A number written as the sum of the values of its digits.'),
                    ('place holder', 'A zero that holds an empty place.'),
                ],
                'example': {
                    'title': 'Worked example: expanding and building 9-digit numbers',
                    'html': (
                        '<p><strong>1. Expand 403 060 025.</strong></p>'
                        '<p>403 060 025 = 400 000 000 + 3 000 000 + 60 000 + 20 + 5</p>'
                        '<p><strong>2. Build 900 000 000 + 50 000 000 + 400 000 + 7 000 + 80.</strong></p>'
                        '<p>Millions group: 950. Thousands group: 407. Units group: 080.</p>'
                        '<p>Answer: <strong>950 407 080</strong></p>'
                        '<p><strong>3. What is the value of 6 in 468 213 579?</strong> The 6 is in the ten millions '
                        'place, so its value is <strong>60 000 000</strong>.</p>'
                    ),
                },
                'video': {'id': 'f3YjmQFSxl0',
                          'title': 'Finding the Value of the Underlined Digit | Whole Number Place Value | Math with Mr. J',
                          'channel': 'Math with Mr. J', 'minutes': 3},
                'worksheet': {
                    'instructions': 'Answer all the questions. Draw a place value table with 9 columns if it helps.',
                    'exercises': [
                        '1. What is the value of the digit 6 in 468 213 579?',
                        '2. What is the value of the digit 3 in 712 534 908?',
                        '3. Write 286 041 735 in expanded notation.',
                        '4. Write as one number: 900 000 000 + 50 000 000 + 400 000 + 7 000 + 80',
                        '5. Which digit is in the hundred thousands place in 851 694 302?',
                        '6. In 770 000 000, how many times bigger is the value of the first 7 than the second 7?',
                        '7. Write the biggest 9-digit number that uses each of the digits 1 to 9 once.',
                    ],
                },
                'quiz': [
                    ('mcq', 'What is the value of the 8 in 182 465 039?',
                     ['8 000 000', '80 000 000', '800 000', '8 000'], 1),
                    ('mcq', 'Which digit is in the millions place in 347 920 615?', ['3', '4', '7', '9'], 2),
                    ('tf', 'In 509 312 480 the value of the 9 is 900 000.', False),
                    ('mcq', 'Which number is 70 000 000 + 6 000 000 + 50 000 + 200?',
                     ['76 500 200', '76 050 200', '706 050 200', '76 005 200'], 1),
                ],
                'homework': {
                    'title': 'Expanded notation with millions',
                    'instructions': 'Show your working.',
                    'tasks': [
                        'Write 624 900 318 and 105 020 007 in expanded notation.',
                        'Build the number: 300 000 000 + 8 000 000 + 90 000 + 400 + 1',
                        'Write the value of every digit in 457 123 869.',
                    ],
                    'marks': 12,
                },
            },
            {
                'title': 'Comparing, ordering and rounding off (5, 10, 100, 1 000)',
                'minutes': 50,
                'objectives': [
                    'I can compare and order numbers up to 9 digits.',
                    'I can round off to the nearest 5, 10, 100 and 1 000.',
                    'I can use rounding to check whether an answer is sensible.',
                ],
                'notes': (
                    '<p><strong>Comparing and ordering</strong></p>'
                    '<ol><li>Count the digits: the number with more digits is bigger. 100 000 000 &gt; 99 999 999.</li>'
                    '<li>Same number of digits? Compare from the left, place by place, until the digits differ.</li></ol>'
                    '<p>512 034 678 &lt; 512 043 678 because the ten thousands digit 3 is less than 4.</p>'
                    '<p><strong>Rounding off to the nearest 10, 100 or 1 000</strong>: look at the digit to the right of the '
                    'place you are rounding to. 5 or more: round up. 4 or less: keep the digit. Then fill in zeros.</p>'
                    '<p><strong>Rounding off to the nearest 5</strong>: look at the units digit.</p>'
                    '<ul><li>1 or 2: round down to 0 (e.g. 432 becomes 430)</li>'
                    '<li>3 or 4: round up to 5 (e.g. 434 becomes 435)</li>'
                    '<li>6 or 7: round down to 5 (e.g. 437 becomes 435)</li>'
                    '<li>8 or 9: round up to the next ten (e.g. 438 becomes 440)</li></ul>'
                    '<p>Rounding helps us <strong>estimate</strong>. If 3 847 263 people live in a region, we can say '
                    '"about 3 847 000" (nearest 1 000).</p>'
                ),
                'key_terms': [
                    ('estimate', 'A sensible guess that is close to the exact answer.'),
                    ('round off', 'Replace a number with a nearby number that is easier to work with.'),
                    ('nearest 5', 'The closest number that ends in 0 or 5.'),
                ],
                'example': {
                    'title': 'Worked example: order and round',
                    'html': (
                        '<p><strong>1. Ascending order: 45 678 901; 4 567 890; 456 789 012; 45 687 901</strong></p>'
                        '<p>4 567 890 has 7 digits (smallest). 456 789 012 has 9 digits (biggest). The two 8-digit numbers: '
                        'compare the ten thousands, 7 &lt; 8.</p>'
                        '<p>Answer: 4 567 890; 45 678 901; 45 687 901; 456 789 012</p>'
                        '<p><strong>2. Round 3 847 263.</strong></p>'
                        '<ul><li>Nearest 5: units digit 3, round up to 5: 3 847 265</li>'
                        '<li>Nearest 10: units 3, round down: 3 847 260</li>'
                        '<li>Nearest 100: tens 6, round up: 3 847 300</li>'
                        '<li>Nearest 1 000: hundreds 2, round down: 3 847 000</li></ul>'
                    ),
                },
                'video': {'id': 'fd-E18EqSVk', 'title': 'Math Antics - Rounding', 'channel': 'mathantics', 'minutes': 11},
                'worksheet': {
                    'instructions': 'Fill in <, > or =, then order and round the numbers.',
                    'exercises': [
                        '1. 98 765 432 ____ 100 000 000',
                        '2. 512 034 678 ____ 512 043 678',
                        '3. Write in ascending order: 20 202 020; 2 020 202; 22 020 200; 20 220 202',
                        '4. Round 6 283 547 to the nearest 5.',
                        '5. Round 6 283 547 to the nearest 10.',
                        '6. Round 6 283 547 to the nearest 100.',
                        '7. Round 6 283 547 to the nearest 1 000.',
                    ],
                },
                'quiz': [
                    ('mcq', 'Which number is the largest?', ['99 999 999', '100 000 001', '100 000 000', '10 999 999'], 1),
                    ('mcq', 'Round 4 736 to the nearest 5.', ['4 730', '4 740', '4 735', '4 700'], 2),
                    ('tf', '7 849 512 rounded to the nearest 1 000 is 7 850 000.', True),
                    ('mcq', 'Which list is in descending order?',
                     ['340 000; 3 040 000; 3 400 000', '3 040 000; 3 400 000; 340 000', '3 400 000; 3 040 000; 340 000'], 2),
                ],
                'homework': {
                    'title': 'Order and round',
                    'instructions': 'Show which digit you looked at each time you rounded.',
                    'tasks': [
                        'Write in descending order: 305 050 500; 350 005 050; 305 500 050; 35 050 500',
                        'Round 18 476 to the nearest 5, 10, 100 and 1 000.',
                        'Round 902 849 to the nearest 5, 10, 100 and 1 000.',
                    ],
                    'marks': 15,
                },
            },
        ],
    },

    # =====================================================================
    # GRADE 4 ENGLISH HOME LANGUAGE
    # =====================================================================
    (4, 'ENG-HL'): {
        'topic': 'Folktales: listening, reading, nouns and writing a paragraph',
        'caps': 'CAPS English HL Gr 4 Term 1, Weeks 1-2: Listening & Speaking - listen to a story/folktale and '
                'answer questions; Reading & Viewing - reading comprehension, story elements; Writing - a '
                'paragraph; Language Structures & Conventions - common and proper nouns, capital letters and full stops',
        'summary': 'Learners listen to and discuss a folktale, read a short story and identify characters, setting '
                   'and plot, then learn about common and proper nouns and write their first paragraph of the year.',
        'days': [
            {
                'title': 'Listening to a folktale',
                'minutes': 45,
                'objectives': [
                    'I can listen carefully to a story and answer questions about it.',
                    'I can say what a folktale is.',
                    'I can retell a story in the correct order.',
                ],
                'notes': (
                    '<p>A <strong>folktale</strong> is a very old story that people told out loud for many years before '
                    'anyone wrote it down. Grandparents told folktales to children around the fire. Folktales often have '
                    '<strong>animals that talk</strong>, and they usually teach a <strong>lesson</strong> (a moral).</p>'
                    '<p><strong>How to be a good listener</strong></p>'
                    '<ul><li>Look at the speaker and sit still.</li>'
                    '<li>Make a picture of the story in your mind.</li>'
                    '<li>Listen for <em>who</em> is in the story, <em>where</em> it happens and <em>what</em> happens.</li>'
                    '<li>Wait until the speaker has finished before you put up your hand.</li></ul>'
                    '<p>Today your teacher (or someone at home) will read the folktale <em>The Tortoise and the Hare</em> '
                    'to you. Listen once for enjoyment. Then listen a second time and think about the questions on the worksheet.</p>'
                    '<p>When you <strong>retell</strong> a story, use order words: <strong>first</strong>, '
                    '<strong>then</strong>, <strong>next</strong>, <strong>after that</strong>, <strong>finally</strong>.</p>'
                ),
                'key_terms': [
                    ('folktale', 'An old story passed on by people telling it out loud.'),
                    ('moral', 'The lesson a story teaches.'),
                    ('retell', 'Tell a story again in your own words, in the right order.'),
                ],
                'example': {
                    'title': 'Listening text: The Tortoise and the Hare',
                    'html': (
                        '<p>Long ago, Hare was always boasting. "I am the fastest animal in the veld!" he said. '
                        '"Nobody can beat me."</p>'
                        '<p>Tortoise was tired of hearing this. "I will race you," she said quietly. All the animals laughed.</p>'
                        '<p>The race started at the big baobab tree. Hare ran so fast that soon Tortoise was far behind. '
                        '"I have lots of time," Hare said, and he lay down under a thorn tree and fell asleep.</p>'
                        '<p>Tortoise kept walking, slowly and steadily. She did not stop once. She walked past the sleeping Hare.</p>'
                        '<p>When Hare woke up, the sun was setting. He ran as fast as he could, but Tortoise was already '
                        'crossing the finish line at the river. The animals cheered for Tortoise.</p>'
                        '<p><em>Moral: Slow and steady wins the race.</em></p>'
                        '<p><strong>Pair activity:</strong> Retell the story to a partner using first, then, next, finally.</p>'
                    ),
                },
                'video': {'id': 'cR01RGN0288', 'title': 'Anansi and the Melon | Folktales | Stories for Kids | Bedtime Stories',
                          'channel': 'Little Fox - Kids Stories and Songs', 'minutes': 4},
                'worksheet': {
                    'instructions': 'Listen to "The Tortoise and the Hare" again. Answer the questions in full sentences.',
                    'exercises': [
                        '1. Who are the two main characters in the story?',
                        '2. Why did Tortoise decide to race Hare?',
                        '3. Where did the race start, and where did it finish?',
                        '4. What did Hare do while Tortoise kept walking?',
                        '5. Who won the race? Why?',
                        '6. What is the moral of the story? Say it in your own words.',
                        '7. Number these in order: Hare falls asleep / The animals cheer / Hare boasts / The race starts.',
                    ],
                },
                'quiz': [
                    ('mcq', 'What is a folktale?',
                     ['A news report', 'An old story passed on by telling it out loud', 'A poem about the sea', 'A list of instructions'], 1),
                    ('tf', 'In the story, Hare fell asleep under a thorn tree.', True),
                    ('mcq', 'Who won the race?', ['Hare', 'Lion', 'Tortoise', 'Nobody'], 2),
                    ('mcq', 'What is the moral of the story?',
                     ['Slow and steady wins the race.', 'Always run fast.', 'Never sleep outside.', 'Big animals are clever.'], 0),
                ],
                'homework': {
                    'title': 'Tell a story at home',
                    'instructions': 'Share a story with someone in your family.',
                    'tasks': [
                        'Retell "The Tortoise and the Hare" to someone at home.',
                        'Ask them to tell you a folktale or story they heard as a child. Write down its title and two things that happened in it.',
                    ],
                    'marks': 10,
                },
            },
            {
                'title': 'Reading a story: characters, setting and plot',
                'minutes': 45,
                'objectives': [
                    'I can read a short story and answer questions about it.',
                    'I can name the characters and the setting of a story.',
                    'I can describe the beginning, middle and end of a story.',
                ],
                'notes': (
                    '<p>Every story has <strong>story elements</strong>. Good readers look for them while they read.</p>'
                    '<ul><li><strong>Characters</strong>: the people or animals in the story. The most important one is '
                    'the <em>main character</em>.</li>'
                    '<li><strong>Setting</strong>: <em>where</em> and <em>when</em> the story happens.</li>'
                    '<li><strong>Plot</strong>: what happens. A plot has a <strong>beginning</strong> (we meet the characters), '
                    'a <strong>middle</strong> (there is a problem) and an <strong>end</strong> (the problem is solved).</li></ul>'
                    '<p><strong>Reading strategies</strong></p>'
                    '<ol><li><em>Before</em> reading: look at the title. What do you think the story is about? (predict)</li>'
                    '<li><em>During</em> reading: stop and ask yourself, "What has happened so far?"</li>'
                    '<li><em>After</em> reading: answer the questions. Look back in the story to find the answers.</li></ol>'
                    '<p>Some answers are written in the story (you can point to them). For others you must think and use '
                    'clues, for example how a character feels.</p>'
                ),
                'key_terms': [
                    ('character', 'A person or animal in a story.'),
                    ('setting', 'Where and when a story takes place.'),
                    ('plot', 'The events of the story: beginning, middle and end.'),
                    ('predict', 'Guess what will happen, using clues.'),
                ],
                'example': {
                    'title': 'Reading text: Lindiwe and the Lost Goat',
                    'html': (
                        '<p>Lindiwe lived with her grandmother in a small village near the hills. Every afternoon after school '
                        'she took the goats to drink at the stream.</p>'
                        '<p>One afternoon she counted the goats. "One, two, three, four ... where is Tiny?" Tiny, the smallest goat, '
                        'was missing! Lindiwe felt her heart beat fast.</p>'
                        '<p>She looked behind the rocks. She looked under the bushes. Then she heard a soft "Meh-eh-eh" from the '
                        'top of the hill. Tiny was stuck between two big stones.</p>'
                        '<p>Lindiwe climbed up carefully, pushed one stone away and lifted Tiny into her arms. When she got home, '
                        'Gogo smiled. "You are a brave girl," she said, and gave Lindiwe a warm cup of tea.</p>'
                        '<p><strong>Class activity:</strong> Draw three boxes: Beginning, Middle, End. Write one sentence in each box.</p>'
                    ),
                },
                'video': {'id': '1M0pFLXegG0',
                          'title': 'Story Elements Part 1: Characters, Setting, and Events | English For Kids | Mind Blooming',
                          'channel': 'Mind Blooming', 'minutes': 2},
                'worksheet': {
                    'instructions': 'Read "Lindiwe and the Lost Goat". Answer the questions in full sentences.',
                    'exercises': [
                        '1. Who is the main character?',
                        '2. Where does the story take place?',
                        '3. What did Lindiwe do every afternoon after school?',
                        '4. What was the problem in the story?',
                        '5. How did Lindiwe feel when she saw that Tiny was missing? How do you know?',
                        '6. How was the problem solved?',
                        '7. Do you think Gogo was proud of Lindiwe? Give a reason.',
                    ],
                },
                'quiz': [
                    ('mcq', 'What is the setting of a story?',
                     ['The people in the story', 'Where and when the story happens', 'The lesson of the story', 'The title'], 1),
                    ('mcq', 'In "Lindiwe and the Lost Goat", where was Tiny found?',
                     ['In the stream', 'Under a bush', 'At school', 'Between two stones on the hill'], 3),
                    ('tf', 'The problem in a story usually happens in the middle.', True),
                    ('mcq', 'Who said, "You are a brave girl"?', ['Gogo', 'Lindiwe', 'The teacher'], 0),
                ],
                'homework': {
                    'title': 'Story elements of a favourite story',
                    'instructions': 'Think of a story you know well (a book, a folktale or a film).',
                    'tasks': [
                        'Write the title and name the main character.',
                        'Describe the setting in one sentence.',
                        'Write one sentence each for the beginning, the middle and the end.',
                    ],
                    'marks': 10,
                },
            },
            {
                'title': 'Common and proper nouns, and writing a paragraph',
                'minutes': 45,
                'objectives': [
                    'I can tell the difference between common nouns and proper nouns.',
                    'I can use capital letters and full stops correctly.',
                    'I can write a paragraph with a topic sentence.',
                ],
                'notes': (
                    '<p>A <strong>noun</strong> is a naming word. It names a person, animal, place or thing.</p>'
                    '<ul><li><strong>Common nouns</strong> name any person, place or thing: <em>girl, goat, village, river, school</em>. '
                    'They start with a small letter (unless they begin a sentence).</li>'
                    '<li><strong>Proper nouns</strong> name a <em>particular</em> person, place or thing: <em>Lindiwe, Durban, '
                    'the Orange River, Monday, January</em>. Proper nouns <strong>always start with a capital letter</strong>.</li></ul>'
                    '<p><strong>Punctuation</strong>: every sentence begins with a <strong>capital letter</strong> and ends with a '
                    '<strong>full stop</strong> (.), a question mark (?) or an exclamation mark (!).</p>'
                    '<p><strong>Writing a paragraph</strong></p>'
                    '<p>A paragraph is a group of sentences about <em>one</em> main idea.</p>'
                    '<ol><li>Start with a <strong>topic sentence</strong> that tells the reader what the paragraph is about.</li>'
                    '<li>Add three or four <strong>supporting sentences</strong> with details.</li>'
                    '<li>End with a <strong>closing sentence</strong>.</li></ol>'
                    '<p>Plan first, then write, then check your capital letters and full stops.</p>'
                ),
                'key_terms': [
                    ('noun', 'A naming word for a person, animal, place or thing.'),
                    ('common noun', 'A general name, e.g. city, dog, teacher.'),
                    ('proper noun', 'A special name that starts with a capital letter, e.g. Cape Town.'),
                    ('topic sentence', 'The first sentence of a paragraph, which gives the main idea.'),
                ],
                'example': {
                    'title': 'Guided writing: My holiday',
                    'html': (
                        '<p><strong>Model paragraph</strong> (proper nouns in bold):</p>'
                        '<p>During the holiday I visited my aunt in <strong>Pietermaritzburg</strong>. On the first day we walked '
                        'in the park and fed the ducks. My cousin <strong>Sipho</strong> taught me to play a new card game. '
                        'On <strong>Christmas</strong> Day the whole family ate lunch together under a big tree. '
                        'It was the best holiday I have ever had.</p>'
                        '<ul><li>Topic sentence: the first sentence tells us the paragraph is about a visit.</li>'
                        '<li>Supporting sentences: three details about the holiday.</li>'
                        '<li>Closing sentence: how the writer felt.</li></ul>'
                        '<p><strong>Your turn:</strong> plan your own paragraph about your holiday in three short notes, then write it.</p>'
                    ),
                },
                'video': {'id': 'YVvYqOZSvYA',
                          'title': 'Nouns - Common and Proper | English Grammar & Composition Grade 4 | Periwinkle',
                          'channel': 'Periwinkle', 'minutes': 2},
                'worksheet': {
                    'instructions': 'Complete the language exercises, then write your paragraph.',
                    'exercises': [
                        '1. Underline the nouns: The girl took the goats to the stream.',
                        '2. Write C (common) or P (proper): river / Limpopo / teacher / Mrs Dlamini / city / Johannesburg',
                        '3. Rewrite with capital letters and a full stop: my friend thabo lives in polokwane',
                        '4. Write a proper noun for each common noun: a day, a month, a country',
                        '5. Rewrite correctly: on monday we went to the beach in durban',
                        '6. Write a paragraph of 5 sentences about your holiday. Start with a topic sentence.',
                    ],
                },
                'quiz': [
                    ('mcq', 'Which word is a proper noun?', ['school', 'mountain', 'Lindiwe', 'goat'], 2),
                    ('tf', 'A common noun always starts with a capital letter.', False),
                    ('mcq', 'Which sentence is written correctly?',
                     ['we live in cape town.', 'We live in Cape Town.', 'We live in cape Town', 'we Live in Cape town.'], 1),
                    ('mcq', 'What does a topic sentence do?',
                     ['It tells the main idea of the paragraph.', 'It is always a question.', 'It ends the story.', 'It lists all the nouns.'], 0),
                ],
                'homework': {
                    'title': 'Noun hunt and paragraph',
                    'instructions': 'Use what you learnt about nouns and paragraphs.',
                    'tasks': [
                        'Find 5 common nouns and 5 proper nouns in a newspaper, magazine or book. Write them in two lists.',
                        'Finish your holiday paragraph and check every capital letter and full stop.',
                    ],
                    'marks': 15,
                },
            },
        ],
    },

    # =====================================================================
    # GRADE 5 ENGLISH HOME LANGUAGE
    # =====================================================================
    (5, 'ENG-HL'): {
        'topic': 'Stories and folktales: active listening, reading for meaning, nouns, verbs and paragraphs',
        'caps': 'CAPS English HL Gr 5 Term 1, Weeks 1-2: Listening & Speaking - listen to a folktale, retell it; '
                'Reading & Viewing - reading comprehension (literal and inferential questions); Writing - a paragraph; '
                'Language Structures & Conventions - nouns (common, proper, collective), verbs and tense, punctuation',
        'summary': 'Learners practise active listening with a southern African folktale, read a short story for '
                   'meaning, revise nouns and verbs, and write a well-structured paragraph.',
        'days': [
            {
                'title': 'Active listening: How the Zebra Got Its Stripes',
                'minutes': 45,
                'objectives': [
                    'I can show that I am listening actively.',
                    'I can answer questions about a folktale I have heard.',
                    'I can retell a story in sequence using linking words.',
                ],
                'notes': (
                    '<p><strong>Active listening</strong> means listening with your whole mind, not just your ears. '
                    'An active listener:</p>'
                    '<ul><li>looks at the speaker and avoids distractions;</li>'
                    '<li>thinks about <em>who, what, where, when, why</em> and <em>how</em> while listening;</li>'
                    '<li>makes short notes of key words (not full sentences);</li>'
                    '<li>asks a question afterwards if something was not clear.</li></ul>'
                    '<p>Today you will listen to a traditional tale told in parts of southern Africa about how the '
                    'zebra got its stripes. Like many folktales, it is a <strong>"why" story</strong>: it gives a '
                    'make-believe explanation for something in nature.</p>'
                    '<p>Listen once for enjoyment. On the second listening, write key words under the headings '
                    '<em>Beginning, Middle, End</em>. Then use your notes to <strong>retell</strong> the story to a partner, '
                    'using linking words such as <em>at first, then, suddenly, after that, in the end</em>.</p>'
                    '<p>When your partner retells, show respect: do not interrupt, and give one kind comment and one tip.</p>'
                ),
                'key_terms': [
                    ('active listening', 'Listening carefully and thinking about what you hear.'),
                    ('key words', 'The most important words that help you remember the message.'),
                    ('"why" story', 'A folktale that explains how something in nature came to be.'),
                ],
                'example': {
                    'title': 'Listening text: How the Zebra Got Its Stripes (a retelling)',
                    'html': (
                        '<p>Long ago, when the sun was very hot and the rivers were drying up, all the animals had pure white coats. '
                        'Only one waterhole was left, and a bad-tempered baboon sat next to it beside his fire. '
                        '"This water is mine," he shouted. "Nobody may drink!"</p>'
                        '<p>One day a thirsty young zebra came to the waterhole. "Please, there is enough water for everyone," '
                        'Zebra said. Baboon only laughed and threw sand at him.</p>'
                        '<p>The two began to fight. With one mighty kick, Zebra sent Baboon flying onto the rocks. But Zebra '
                        'stumbled backwards through the fire, and the burning sticks left black stripes all over his white coat.</p>'
                        '<p>Zebra was so surprised that he galloped off to the open plains, where zebras still live today. '
                        'And Baboon? He landed so hard on the rocks that, the story says, baboons still have a bare patch where they sit.</p>'
                        '<p><strong>Pair activity:</strong> Retell the story using your key-word notes.</p>'
                    ),
                },
                'video': {'id': '0nmJW_zExk0',
                          'title': "Active listening is a skill! Here's how it's done. | What's Your Story? | Heartlines",
                          'channel': 'HeartlinesZA', 'minutes': 2},
                'worksheet': {
                    'instructions': 'Use your listening notes to answer the questions in full sentences.',
                    'exercises': [
                        '1. What colour were all the animals at the beginning of the story?',
                        '2. Why was the waterhole so important?',
                        '3. How did Baboon behave? Give two examples.',
                        '4. How did Zebra get his stripes?',
                        '5. What happened to Baboon at the end?',
                        '6. Why do we call this a "why" story?',
                        '7. Write three linking words you used when you retold the story.',
                    ],
                },
                'quiz': [
                    ('tf', 'An active listener makes notes of key words while listening.', True),
                    ('mcq', 'In the story, what made the black stripes on Zebra?',
                     ['Mud from the river', 'Burning sticks from the fire', 'Paint', 'Baboon drew them'], 1),
                    ('mcq', 'What does a "why" story do?',
                     ['Gives the news', 'Gives instructions', 'Explains something in nature in a make-believe way', 'Describes a real scientist'], 2),
                    ('mcq', 'Which of these is a linking word for retelling?', ['Suddenly', 'Zebra', 'Thirsty', 'Water'], 0),
                ],
                'homework': {
                    'title': 'Listen and retell',
                    'instructions': 'Practise active listening at home.',
                    'tasks': [
                        'Ask an adult to tell you a story or describe a special day from their childhood. Make key-word notes while you listen.',
                        'Use your notes to write 5 sentences retelling what you heard. Use at least 3 linking words.',
                    ],
                    'marks': 10,
                },
            },
            {
                'title': 'Reading for meaning: literal and inferential questions',
                'minutes': 45,
                'objectives': [
                    'I can read a story and answer literal questions.',
                    'I can answer inferential questions using clues from the text.',
                    'I can identify the main character, setting and problem.',
                ],
                'notes': (
                    '<p>When we read, we answer two kinds of questions.</p>'
                    '<ul><li><strong>Literal questions</strong> ("right there" questions): the answer is written in the text. '
                    'You can put your finger on it. <em>Example: What was the name of the new school?</em></li>'
                    '<li><strong>Inferential questions</strong> ("think and search" questions): the answer is not written '
                    'directly. You use <strong>clues</strong> in the text plus what you already know. '
                    '<em>Example: How did Mpho feel on her first morning? How do you know?</em></li></ul>'
                    '<p>When you answer an inferential question, give your answer <strong>and</strong> the clue: '
                    '"I think she was nervous <em>because</em> her hands were shaking."</p>'
                    '<p><strong>Reading strategy (SQ3R in short)</strong></p>'
                    '<ol><li><em>Survey</em>: look at the title and pictures.</li>'
                    '<li><em>Question</em>: ask what you want to find out.</li>'
                    '<li><em>Read</em> the text carefully.</li>'
                    '<li><em>Recite</em>: say the main points in your own words.</li>'
                    '<li><em>Review</em>: read again to check your answers.</li></ol>'
                    '<p>Always answer in full sentences and use your own words where you can.</p>'
                ),
                'key_terms': [
                    ('literal', 'The answer is stated in the text.'),
                    ('inferential', 'The answer must be worked out from clues.'),
                    ('clue', 'A detail in the text that helps you work something out.'),
                ],
                'example': {
                    'title': "Reading text: Mpho's First Day",
                    'html': (
                        '<p>Mpho stood at the gate of Sunrise Primary School and held her bag tightly. Her hands were shaking. '
                        'Her family had moved to a new town during the holidays, and she did not know a single person here.</p>'
                        '<p>In the classroom, the teacher, Mr Naidoo, smiled. "Class, this is Mpho. Who will show her around?" '
                        'A tall boy with a big smile put up his hand. "I will, sir. I am Kagiso."</p>'
                        '<p>At break, Kagiso showed Mpho the library, the tuck shop and the netball court. "Do you play netball?" '
                        'he asked. Mpho\'s eyes lit up. "I was the goal shooter at my old school!"</p>'
                        '<p>By the time the bell rang at the end of the day, Mpho was laughing with three new friends. '
                        'She walked out of the gate swinging her bag.</p>'
                        '<p><strong>Discuss:</strong> Which questions below are literal (L) and which are inferential (I)?</p>'
                    ),
                },
                'video': {'id': 'Ugi5KYfQO-0', 'title': 'Anansi And Turtle go to Dinner (Animated Stories for Kids)',
                          'channel': 'August House/Story Cove', 'minutes': 6},
                'worksheet': {
                    'instructions': "Read \"Mpho's First Day\". Write L or I next to each question number, then answer it.",
                    'exercises': [
                        '1. What is the name of Mpho\'s new school?',
                        '2. Why did Mpho not know anyone at the school?',
                        '3. How did Mpho feel at the gate in the morning? Give a clue from the text.',
                        '4. Name two places Kagiso showed Mpho.',
                        '5. What position did Mpho play in netball at her old school?',
                        '6. How did Mpho feel at the end of the day? Give a clue from the text.',
                        '7. What kind of person is Kagiso? Give a reason for your answer.',
                    ],
                },
                'quiz': [
                    ('mcq', 'Which question is a literal question about the story?',
                     ['Why was Mpho nervous?', 'What is the name of the teacher?', 'What kind of person is Kagiso?', 'Will Mpho be happy at this school?'], 1),
                    ('tf', 'To answer an inferential question, you use clues from the text.', True),
                    ('mcq', 'Which clue shows that Mpho was happy at the end of the day?',
                     ['She held her bag tightly.', 'Her hands were shaking.', 'She walked out swinging her bag.', 'She stood at the gate.'], 2),
                    ('mcq', 'Who offered to show Mpho around?', ['Kagiso', 'Mr Naidoo', 'Her mother', 'The principal'], 0),
                ],
                'homework': {
                    'title': 'Write your own questions',
                    'instructions': 'Choose a short story or a page from a book at home.',
                    'tasks': [
                        'Read it carefully and write 2 literal questions and 2 inferential questions about it.',
                        'Answer your inferential questions in full sentences, giving a clue for each.',
                    ],
                    'marks': 12,
                },
            },
            {
                'title': 'Nouns, verbs and writing a paragraph',
                'minutes': 45,
                'objectives': [
                    'I can identify common, proper and collective nouns.',
                    'I can identify verbs and write them in the present and past tense.',
                    'I can write a paragraph with a topic sentence, supporting sentences and a closing sentence.',
                ],
                'notes': (
                    '<p><strong>Nouns</strong> are naming words.</p>'
                    '<ul><li><strong>Common nouns</strong>: school, friend, bag</li>'
                    '<li><strong>Proper nouns</strong> (capital letter): Mpho, Kagiso, Mr Naidoo, January</li>'
                    '<li><strong>Collective nouns</strong> name a group: a <em>herd</em> of zebras, a <em>team</em> of players, '
                    'a <em>class</em> of learners, a <em>flock</em> of sheep</li></ul>'
                    '<p><strong>Verbs</strong> are doing (action) words or being words: <em>run, read, kick, is, was</em>. '
                    'Every sentence needs a verb.</p>'
                    '<p>The <strong>tense</strong> of a verb tells us <em>when</em> something happens:</p>'
                    '<ul><li>Present tense: Mpho <em>walks</em> to school.</li>'
                    '<li>Past tense: Mpho <em>walked</em> to school.</li></ul>'
                    '<p>Many verbs add <strong>-ed</strong> for the past tense (play, played). Some are irregular: '
                    'run, ran; go, went; see, saw; eat, ate.</p>'
                    '<p><strong>A good paragraph</strong> has one main idea: a <strong>topic sentence</strong>, three or four '
                    '<strong>supporting sentences</strong> and a <strong>closing sentence</strong>. When writing about something '
                    'that has already happened, keep your verbs in the <strong>past tense</strong>.</p>'
                ),
                'key_terms': [
                    ('collective noun', 'A noun that names a group, e.g. herd, team, flock.'),
                    ('verb', 'A doing or being word.'),
                    ('tense', 'The form of a verb that shows when an action happens.'),
                    ('irregular verb', 'A verb that does not add -ed in the past tense, e.g. go / went.'),
                ],
                'example': {
                    'title': 'Guided writing: The best day of my holiday',
                    'html': (
                        '<p><strong>Plan</strong>: Where? (the beach) Who? (my family) What happened? (swam, built a sandcastle, saw dolphins)</p>'
                        '<p><strong>Paragraph</strong> (verbs in bold):</p>'
                        '<p>The best day of my holiday <strong>was</strong> the day we <strong>went</strong> to the beach. '
                        'My family <strong>left</strong> home early and <strong>packed</strong> a picnic. My brother and I '
                        '<strong>built</strong> a huge sandcastle with a moat. Later we <strong>saw</strong> a pod of dolphins '
                        'jumping in the waves. I <strong>will</strong> never forget that wonderful day.</p>'
                        '<p>Notice the collective noun <em>pod</em> (a group of dolphins), and that the verbs are in the past tense.</p>'
                    ),
                },
                'video': {'id': 'kw9GOUqSc5M', 'title': 'How to Write a Paragraph for Kids (Grades 3-5)',
                          'channel': 'Ms. Andy', 'minutes': 6},
                'worksheet': {
                    'instructions': 'Complete the language exercises, then write your paragraph.',
                    'exercises': [
                        '1. Write the collective noun: a ____ of sheep; a ____ of players; a ____ of zebras',
                        '2. Write C (common) or P (proper): Kagiso / netball / Durban / library / February',
                        '3. Underline the verbs: Kagiso smiled and showed Mpho the library.',
                        '4. Change to the past tense: I go to school and I see my friends.',
                        '5. Change to the present tense: She ran to the gate and ate her lunch.',
                        '6. Write a paragraph of 5-6 sentences about the best day of your holiday. Underline your topic sentence.',
                    ],
                },
                'quiz': [
                    ('mcq', 'Which is a collective noun?', ['run', 'herd', 'Durban', 'happy'], 1),
                    ('mcq', 'What is the past tense of "go"?', ['goed', 'gone', 'goes', 'went'], 3),
                    ('tf', 'In the sentence "The team played well", the verb is "played".', True),
                    ('mcq', 'Which sentence is in the present tense?',
                     ['Mpho walks to school.', 'Mpho walked to school.', 'Mpho will walk to school.'], 0),
                ],
                'homework': {
                    'title': 'Verbs and nouns in action',
                    'instructions': 'Complete in your homework book.',
                    'tasks': [
                        'Write 5 sentences about what you did yesterday. Underline every verb (they should be in the past tense).',
                        'Write the collective noun for: bees, cattle, singers, fish.',
                        'Finish and neaten your holiday paragraph.',
                    ],
                    'marks': 15,
                },
            },
        ],
    },

    # =====================================================================
    # GRADE 6 ENGLISH HOME LANGUAGE
    # =====================================================================
    (6, 'ENG-HL'): {
        'topic': 'Folktales and narratives: listening for detail, story elements, nouns and direct speech',
        'caps': 'CAPS English HL Gr 6 Term 1, Weeks 1-2: Listening & Speaking - listen to a folktale for main idea '
                'and details; Reading & Viewing - reading comprehension, story elements (character, setting, plot, '
                'conflict, theme); Writing - a narrative paragraph; Language Structures & Conventions - kinds of nouns, '
                'punctuation of direct speech',
        'summary': 'Learners listen to an Anansi folktale and take notes, read a narrative and analyse conflict, '
                   'character and theme, and learn kinds of nouns and how to punctuate direct speech in their own writing.',
        'days': [
            {
                'title': 'Listening for main idea and details: Anansi and the Pot of Wisdom',
                'minutes': 50,
                'objectives': [
                    'I can listen to a folktale and identify the main idea and supporting details.',
                    'I can take notes in a simple mind map while listening.',
                    'I can explain the moral of a story and give my opinion of it.',
                ],
                'notes': (
                    '<p><strong>Anansi the spider</strong> is a famous trickster character from West African folktales '
                    '(especially from the Akan people of Ghana). His stories travelled across the world and are still told today.</p>'
                    '<p>When you listen to a story, separate the <strong>main idea</strong> (what the whole story is about) '
                    'from the <strong>supporting details</strong> (the events and descriptions that build it).</p>'
                    '<p><strong>Note-taking while you listen</strong></p>'
                    '<ul><li>Draw a circle in the middle of a page and write the title in it.</li>'
                    '<li>Draw branches for <em>Characters</em>, <em>Setting</em>, <em>Problem</em>, <em>Events</em> and <em>Ending/Moral</em>.</li>'
                    '<li>Write only key words on each branch. Use abbreviations (e.g. "A." for Anansi).</li></ul>'
                    '<p>After listening, use your mind map to answer questions and to <strong>discuss</strong> the moral in a group. '
                    'In a discussion, take turns, build on what others say ("I agree with Lerato because ..."), and disagree '
                    'politely ("I see it differently because ...").</p>'
                    '<p>The video tells another Anansi story. Compare: what does Anansi do in both stories?</p>'
                ),
                'key_terms': [
                    ('main idea', 'What the whole text is mostly about.'),
                    ('supporting details', 'Facts or events that explain or build the main idea.'),
                    ('trickster', 'A clever character who plays tricks, often getting into trouble.'),
                    ('mind map', 'A diagram of key words linked to a central topic.'),
                ],
                'example': {
                    'title': 'Listening text: Anansi and the Pot of Wisdom (a retelling)',
                    'html': (
                        '<p>Long ago, Anansi the spider decided he wanted to be the wisest creature on earth. He went around the '
                        'village and collected every bit of wisdom he could find. He stuffed it all into a large clay pot and sealed it.</p>'
                        '<p>"If I hide this pot at the top of the tallest tree," he thought, "nobody else will ever be wise." '
                        'He tied the pot to his front and began to climb. But the pot kept bumping against the trunk, and he slipped '
                        'again and again.</p>'
                        '<p>His young son, Ntikuma, was watching. "Father," he called, "why don\'t you tie the pot to your back? '
                        'Then you can hold the tree."</p>'
                        '<p>Anansi was furious. He had all the wisdom in the world, yet a small child had a better idea! In his anger he '
                        'let go of the pot. It crashed to the ground and broke, and the wisdom was carried away by the wind and the rain '
                        'to every corner of the earth.</p>'
                        '<p>That is why, the story says, no one person has all the wisdom: everyone has a little, and we share it.</p>'
                    ),
                },
                'video': {'id': 'Ti-DYdzPBvM',
                          'title': 'Anansi and the Stolen Drums | African Folktale for Kids | Animated Bedtime Story from Mama Didi',
                          'channel': "Mama Didi's Folktales", 'minutes': 6},
                'worksheet': {
                    'instructions': 'Use your mind map to answer the questions in full sentences.',
                    'exercises': [
                        '1. Write the main idea of the story in one sentence.',
                        '2. What did Anansi want, and what did he do to get it?',
                        '3. Why did Anansi keep slipping while he climbed?',
                        '4. What advice did Ntikuma give his father?',
                        '5. Why was Anansi so angry? Explain the irony (the surprising twist).',
                        '6. What happened to the wisdom at the end?',
                        '7. Do you agree with the moral? Give a reason for your opinion.',
                    ],
                },
                'quiz': [
                    ('mcq', 'What did Anansi collect in the pot?', ['Gold', 'Water', 'Wisdom', 'Honey'], 2),
                    ('tf', 'Anansi\'s son suggested tying the pot to his back.', True),
                    ('mcq', 'What is the main idea of the story?',
                     ['Spiders are good climbers.', 'No one person has all the wisdom; it is shared by everyone.',
                      'Pots break easily.', 'Children should not watch their parents.'], 1),
                    ('mcq', 'What kind of character is Anansi usually?', ['A trickster', 'A king', 'A teacher', 'A hunter'], 0),
                ],
                'homework': {
                    'title': 'Comparing two Anansi stories',
                    'instructions': 'Think about the story we listened to and the Anansi video.',
                    'tasks': [
                        'Write a paragraph (5-7 sentences) comparing Anansi\'s behaviour in the two stories.',
                        'Explain whether you think Anansi is a good role model and why.',
                    ],
                    'marks': 10,
                },
            },
            {
                'title': 'Reading a narrative: conflict, character and theme',
                'minutes': 50,
                'objectives': [
                    'I can identify the conflict, climax and resolution in a narrative.',
                    'I can describe a character\'s traits and support them with evidence.',
                    'I can identify the theme of a story.',
                ],
                'notes': (
                    '<p>In Grade 6 we look more deeply at <strong>story elements</strong>.</p>'
                    '<ul><li><strong>Characters</strong>: we describe them using <em>character traits</em> (honest, stubborn, kind). '
                    'We prove a trait with <strong>evidence</strong> from the text: what the character says, does or thinks.</li>'
                    '<li><strong>Setting</strong>: time and place. The setting can create a mood (e.g. a dark, stormy night feels tense).</li>'
                    '<li><strong>Plot</strong>: introduction, <strong>conflict</strong> (the problem), rising action, '
                    '<strong>climax</strong> (the most exciting or important moment), and <strong>resolution</strong> (how it ends).</li>'
                    '<li><strong>Conflict</strong> can be between two characters, between a character and nature, or inside a '
                    'character\'s own mind (a difficult choice).</li>'
                    '<li><strong>Theme</strong>: the big message or lesson about life, e.g. "honesty takes courage".</li></ul>'
                    '<p>Use the <strong>PEE</strong> structure for longer answers: make a <strong>P</strong>oint, give '
                    '<strong>E</strong>vidence from the text, then <strong>E</strong>xplain how the evidence proves your point.</p>'
                ),
                'key_terms': [
                    ('conflict', 'The problem or struggle in a story.'),
                    ('climax', 'The turning point; the most intense moment of the story.'),
                    ('resolution', 'How the conflict is solved at the end.'),
                    ('theme', 'The main message about life in a story.'),
                    ('character trait', 'A word that describes what a character is like.'),
                ],
                'example': {
                    'title': 'Reading text: The Broken Window',
                    'html': (
                        '<p>The ball flew off Sizwe\'s foot, high over the fence, and smashed straight through Mrs Pillay\'s kitchen window. '
                        'For a moment the whole street was silent.</p>'
                        '<p>"Run!" shouted Jabu. The other boys disappeared around the corner. Sizwe stood frozen. His heart pounded. '
                        'Nobody had seen who kicked the ball. He could run too, and nobody would ever know.</p>'
                        '<p>Instead, he walked slowly up Mrs Pillay\'s path, his legs feeling like jelly, and knocked on the door. '
                        '"Mrs Pillay, it was me. I am very sorry. I will help to pay for the glass."</p>'
                        '<p>Mrs Pillay looked at the broken glass, then at Sizwe. "Most boys would have run away," she said. '
                        '"You can wash my car on Saturdays until it is paid off. And then, perhaps, you can keep washing it for pocket money."</p>'
                        '<p><strong>PEE model answer:</strong> Sizwe is honest (point). He says, "Mrs Pillay, it was me" (evidence). '
                        'Even though nobody saw him, he chose to tell the truth (explanation).</p>'
                    ),
                },
                'video': {'id': 'MPtcV4tSByg',
                          'title': '#6 Elements of a Story--Characters, Setting, Plot & Theme (Reading Comprehension)',
                          'channel': 'Mister Messinger', 'minutes': 6},
                'worksheet': {
                    'instructions': 'Read "The Broken Window" and answer the questions. Use PEE for questions 4 and 7.',
                    'exercises': [
                        '1. Where is the story set?',
                        '2. What is the main conflict for Sizwe? Is it with another person, with nature or inside himself?',
                        '3. What is the climax of the story?',
                        '4. Describe Sizwe\'s character using one trait. Give evidence and explain.',
                        '5. Find a phrase that shows Sizwe was nervous.',
                        '6. How is the conflict resolved?',
                        '7. What is the theme of the story? Explain how the story shows it.',
                    ],
                },
                'quiz': [
                    ('mcq', 'What is the climax of a story?',
                     ['The first sentence', 'The most important or exciting turning point', 'The list of characters', 'The title'], 1),
                    ('mcq', 'In "The Broken Window", what kind of conflict does Sizwe face?',
                     ['A conflict with nature', 'A conflict with a wild animal', 'A conflict inside himself about what to do', 'No conflict'], 2),
                    ('tf', 'The theme of a story is the same as its setting.', False),
                    ('mcq', 'Which trait best describes Sizwe?', ['Honest', 'Lazy', 'Rude', 'Greedy'], 0),
                ],
                'homework': {
                    'title': 'Character study',
                    'instructions': 'Choose a character from any book, story or film you know well.',
                    'tasks': [
                        'Name the character and describe the main conflict they face.',
                        'Write two PEE paragraphs, each about one character trait.',
                    ],
                    'marks': 12,
                },
            },
            {
                'title': 'Kinds of nouns and punctuating direct speech',
                'minutes': 50,
                'objectives': [
                    'I can identify common, proper, collective and abstract nouns.',
                    'I can punctuate direct speech correctly.',
                    'I can write a narrative paragraph that includes dialogue.',
                ],
                'notes': (
                    '<p><strong>Kinds of nouns</strong></p>'
                    '<ul><li><strong>Common</strong>: window, ball, street</li>'
                    '<li><strong>Proper</strong> (capital letter): Sizwe, Mrs Pillay, Saturday, Ghana</li>'
                    '<li><strong>Collective</strong> (a group): a <em>team</em> of players, a <em>crowd</em> of people, a <em>swarm</em> of bees</li>'
                    '<li><strong>Abstract</strong> (things you cannot see or touch: feelings, ideas, qualities): '
                    '<em>honesty, courage, fear, wisdom, friendship</em></li></ul>'
                    '<p><strong>Direct speech</strong> gives the exact words a character says. The rules:</p>'
                    '<ol><li>Put inverted commas (" ") around the spoken words only.</li>'
                    '<li>Start the spoken words with a capital letter.</li>'
                    '<li>Put the punctuation (comma, full stop, question mark or exclamation mark) <em>inside</em> the closing inverted commas.</li>'
                    '<li>Use a comma to separate the speech from "he said" or "she asked".</li>'
                    '<li>Start a <strong>new line</strong> each time a new person speaks.</li></ol>'
                    '<p>Examples:</p>'
                    '<ul><li>"Run!" shouted Jabu.</li>'
                    '<li>Sizwe said, "It was me."</li>'
                    '<li>"Will you help me?" asked Mrs Pillay.</li></ul>'
                    '<p>Dialogue makes a narrative come alive, but use it for important moments only.</p>'
                ),
                'key_terms': [
                    ('abstract noun', 'A noun for a feeling, idea or quality, e.g. courage.'),
                    ('collective noun', 'A noun for a group, e.g. swarm.'),
                    ('direct speech', 'The exact words someone says, inside inverted commas.'),
                    ('inverted commas', 'The marks " " placed around direct speech (also called quotation marks).'),
                ],
                'example': {
                    'title': 'Worked example: fixing direct speech',
                    'html': (
                        '<p><strong>Incorrect:</strong> where is my bag asked Thandi</p>'
                        '<p><strong>Steps:</strong> find the exact spoken words (where is my bag), put inverted commas around them, '
                        'start with a capital, add the question mark inside the inverted commas.</p>'
                        '<p><strong>Correct:</strong> "Where is my bag?" asked Thandi.</p>'
                        '<p><strong>Incorrect:</strong> Mom said we are leaving now</p>'
                        '<p><strong>Correct:</strong> Mom said, "We are leaving now."</p>'
                        '<p><strong>Class activity:</strong> In pairs, write a four-line conversation between two friends on the first '
                        'day of school. Start a new line for each speaker and check every punctuation mark.</p>'
                    ),
                },
                'video': {'id': 's8a19kuole0', 'title': 'Using Speech Marks | Punctuating Direct Speech | EasyTeaching',
                          'channel': 'EasyTeaching', 'minutes': 5},
                'worksheet': {
                    'instructions': 'Complete the language exercises, then write your narrative paragraph.',
                    'exercises': [
                        '1. Sort the nouns into common, proper, collective and abstract: courage, Limpopo, herd, desk, friendship, Thursday, crowd, pencil',
                        '2. Write the abstract noun formed from: brave, honest, happy, wise',
                        '3. Punctuate: please close the door said the teacher',
                        '4. Punctuate: Lerato asked are we writing a test today',
                        '5. Punctuate: watch out shouted Jabu',
                        '6. Write a narrative paragraph (8-10 lines) about an unexpected event. Include at least two lines of correctly punctuated direct speech.',
                    ],
                },
                'quiz': [
                    ('mcq', 'Which word is an abstract noun?', ['table', 'courage', 'Cape Town', 'flock'], 1),
                    ('mcq', 'Which sentence is punctuated correctly?',
                     ['"Where are you going?" asked Gogo.', '"Where are you going" asked Gogo?',
                      'Where are you going? "asked Gogo."', '"where are you going?" asked Gogo.'], 0),
                    ('tf', 'When a new person speaks in a story, we start a new line.', True),
                    ('mcq', 'Which is a collective noun?', ['swarm', 'buzz', 'honey', 'sweetness'], 0),
                    ('tf', 'In direct speech, the full stop goes outside the closing inverted commas.', False),
                ],
                'homework': {
                    'title': 'Dialogue writing',
                    'instructions': 'Use correct direct-speech punctuation throughout.',
                    'tasks': [
                        'Write a conversation of 6-8 lines between you and a family member about your first day back at school.',
                        'Underline every abstract noun you used, and circle every proper noun.',
                    ],
                    'marks': 15,
                },
            },
        ],
    },

    # =====================================================================
    # GRADE 4 ISIZULU FIRST ADDITIONAL LANGUAGE
    # =====================================================================
    (4, 'ZUL-FAL'): {
        'topic': 'Ukubingelela nokuzethula: greetings, introducing yourself and my family',
        'caps': 'CAPS isiZulu FAL Gr 4 Term 1, Weeks 1-2: Ukulalela nokukhuluma (listening & speaking) - '
                'greetings and responses, introducing yourself (ukuzethula), talking about family (umndeni); '
                'simple dialogues; vocabulary with English meanings',
        'summary': 'Learners greet and respond in isiZulu, introduce themselves (name, age, grade, home) and '
                   'name the members of their family, practising in short dialogues.',
        'days': [
            {
                'title': 'Ukubingelela: greeting and responding',
                'minutes': 40,
                'objectives': [
                    'I can greet one person (Sawubona) and a group or an elder (Sanibonani).',
                    'I can ask how someone is and answer (Unjani? Ngiyaphila).',
                    'I can say thank you and goodbye.',
                ],
                'notes': (
                    '<p>In isiZulu, greeting someone is very important and shows <strong>respect</strong> (inhlonipho).</p>'
                    '<ul><li><strong>Sawubona</strong> = Hello (to one person). Reply: <strong>Yebo, sawubona</strong>.</li>'
                    '<li><strong>Sanibonani</strong> = Hello (to two or more people, or respectfully to an elder). '
                    'Reply: <strong>Yebo, sanibonani</strong>.</li>'
                    '<li><strong>Unjani?</strong> = How are you? (one person)</li>'
                    '<li><strong>Ninjani?</strong> = How are you? (more than one person)</li>'
                    '<li><strong>Ngiyaphila</strong> = I am well. <strong>Siyaphila</strong> = We are well.</li>'
                    '<li><strong>Wena unjani?</strong> = And you, how are you?</li>'
                    '<li><strong>Ngiyabonga</strong> = Thank you (I thank). <strong>Siyabonga</strong> = We thank you.</li></ul>'
                    '<p><strong>Saying goodbye</strong> depends on who is leaving:</p>'
                    '<ul><li>The person <em>leaving</em> says <strong>Sala kahle</strong> (Stay well).</li>'
                    '<li>The person <em>staying</em> says <strong>Hamba kahle</strong> (Go well).</li></ul>'
                    '<p>When you greet your teacher, say <strong>Sawubona, thisha</strong> or, more respectfully, '
                    '<strong>Sanibonani, thisha</strong>.</p>'
                ),
                'key_terms': [
                    ('Sawubona', 'Hello (to one person)'),
                    ('Sanibonani', 'Hello (to many people / respectful)'),
                    ('Unjani?', 'How are you?'),
                    ('Ngiyaphila', 'I am well'),
                    ('Ngiyabonga', 'Thank you'),
                    ('Sala kahle / Hamba kahle', 'Stay well / Go well (goodbye)'),
                ],
                'example': {
                    'title': 'Dialogue: Ekuseni esikoleni (In the morning at school)',
                    'html': (
                        '<p><strong>Thabo:</strong> Sawubona, Zinhle! <em>(Hello, Zinhle!)</em><br>'
                        '<strong>Zinhle:</strong> Yebo, sawubona, Thabo. Unjani? <em>(Hello, Thabo. How are you?)</em><br>'
                        '<strong>Thabo:</strong> Ngiyaphila, ngiyabonga. Wena unjani? <em>(I am well, thank you. And you?)</em><br>'
                        '<strong>Zinhle:</strong> Nami ngiyaphila. <em>(I am also well.)</em></p>'
                        '<p><strong>Thisha:</strong> Sanibonani, bafundi! <em>(Hello, learners!)</em><br>'
                        '<strong>Abafundi:</strong> Yebo, sanibonani, thisha! <em>(Hello, teacher!)</em></p>'
                        '<p><strong>Activity:</strong> Walk around the class and greet five classmates. Use Sawubona, Unjani? '
                        'and Ngiyaphila. When you go back to your desk, say Sala kahle!</p>'
                    ),
                },
                'video': {'id': 'A6o5Mrrd4Ww', 'title': 'Learn isiZulu Greetings | How to Greet & Respond in Zulu for Beginners',
                          'channel': 'Zulu Lessons with Thando', 'minutes': 7},
                'worksheet': {
                    'instructions': 'Write the isiZulu words. Use the notes to help you.',
                    'exercises': [
                        '1. How do you say "Hello" to one friend?',
                        '2. How do you say "Hello" to the whole class?',
                        '3. Your friend asks "Unjani?" Write your answer.',
                        '4. What does "Ngiyabonga" mean in English?',
                        '5. You are leaving your friend\'s house. What do you say: Sala kahle or Hamba kahle?',
                        '6. Complete the dialogue: A: Sawubona! B: Yebo, ________. Unjani? A: ________, ngiyabonga.',
                    ],
                },
                'quiz': [
                    ('mcq', 'What do you say to greet ONE person?', ['Sanibonani', 'Sawubona', 'Ngiyabonga', 'Hamba kahle'], 1),
                    ('mcq', 'What does "Ngiyaphila" mean?', ['Thank you', 'Goodbye', 'I am well', 'How are you?'], 2),
                    ('tf', 'The person who is leaving says "Sala kahle".', True),
                    ('mcq', 'Which greeting do you use for a group of people?', ['Sanibonani', 'Sawubona', 'Unjani'], 0),
                ],
                'homework': {
                    'title': 'Greet your family in isiZulu',
                    'instructions': 'Practise greeting at home.',
                    'tasks': [
                        'Greet three people at home in isiZulu and ask them how they are. Write down what you said.',
                        'Draw two people greeting each other and write their speech bubbles in isiZulu.',
                    ],
                    'marks': 10,
                },
            },
            {
                'title': 'Ukuzethula: introducing yourself',
                'minutes': 40,
                'objectives': [
                    'I can say my name, age and grade in isiZulu.',
                    'I can say where I live.',
                    'I can ask a classmate questions to get to know them.',
                ],
                'notes': (
                    '<p><strong>Ukuzethula</strong> means "to introduce yourself". Learn these questions and answers:</p>'
                    '<ul><li><strong>Ngubani igama lakho?</strong> = What is your name?<br>'
                    '<strong>Igama lami nguThabo.</strong> = My name is Thabo.</li>'
                    '<li><strong>Uneminyaka emingaki?</strong> = How old are you?<br>'
                    '<strong>Ngineminyaka eyisishiyagalolunye.</strong> = I am nine years old.<br>'
                    '<strong>Ngineminyaka eyishumi.</strong> = I am ten years old.</li>'
                    '<li><strong>Ufunda ibanga lesingaki?</strong> = Which grade are you in?<br>'
                    '<strong>Ngifunda ibanga lesine.</strong> = I am in Grade 4.</li>'
                    '<li><strong>Uhlala kuphi?</strong> = Where do you live?<br>'
                    '<strong>Ngihlala eThekwini.</strong> = I live in Durban. (eGoli = in Johannesburg)</li></ul>'
                    '<p>When you meet someone new you can say <strong>Ngiyajabula ukukwazi</strong> = I am happy to meet you.</p>'
                    '<p>Notice: <em>ngi-</em> at the start of a verb means <strong>I</strong> (ngi<em>hlala</em> = I live), and '
                    '<em>u-</em> means <strong>you</strong> (u<em>hlala</em> = you live).</p>'
                ),
                'key_terms': [
                    ('Ngubani igama lakho?', 'What is your name?'),
                    ('Igama lami ngu...', 'My name is ...'),
                    ('Uneminyaka emingaki?', 'How old are you?'),
                    ('Uhlala kuphi?', 'Where do you live?'),
                    ('ibanga', 'grade'),
                ],
                'example': {
                    'title': 'Dialogue: Umfundi omusha (A new learner)',
                    'html': (
                        '<p><strong>Zinhle:</strong> Sawubona! Ngubani igama lakho? <em>(Hello! What is your name?)</em><br>'
                        '<strong>Lwazi:</strong> Igama lami nguLwazi. Wena? <em>(My name is Lwazi. And you?)</em><br>'
                        '<strong>Zinhle:</strong> Igama lami nguZinhle. Uneminyaka emingaki? <em>(My name is Zinhle. How old are you?)</em><br>'
                        '<strong>Lwazi:</strong> Ngineminyaka eyishumi. <em>(I am ten years old.)</em><br>'
                        '<strong>Zinhle:</strong> Uhlala kuphi? <em>(Where do you live?)</em><br>'
                        '<strong>Lwazi:</strong> Ngihlala eGoli. Ngiyajabula ukukwazi! <em>(I live in Johannesburg. Happy to meet you!)</em></p>'
                        '<p><strong>Activity:</strong> Practise the dialogue with a partner using your own name, age and town.</p>'
                    ),
                },
                'video': {'id': 'b-hesz7uK_U', 'title': 'Introducing yourself',
                          'channel': 'IsiZulu Tutoring with Teacher Ximba', 'minutes': 6},
                'worksheet': {
                    'instructions': 'Answer in isiZulu. Write full sentences.',
                    'exercises': [
                        '1. Ngubani igama lakho?',
                        '2. Uneminyaka emingaki?',
                        '3. Ufunda ibanga lesingaki?',
                        '4. Uhlala kuphi?',
                        '5. Write the English meaning: Ngiyajabula ukukwazi.',
                        '6. Write three sentences to introduce yourself (name, age, where you live).',
                    ],
                },
                'quiz': [
                    ('mcq', 'What does "Ngubani igama lakho?" mean?',
                     ['Where do you live?', 'How old are you?', 'What is your name?', 'How are you?'], 2),
                    ('mcq', 'How do you say "I am in Grade 4"?',
                     ['Ngifunda ibanga lesine.', 'Ngihlala eThekwini.', 'Ngineminyaka eyishumi.', 'Ngiyaphila.'], 0),
                    ('tf', '"Ngihlala eGoli" means "I live in Johannesburg".', True),
                    ('mcq', 'Which question asks "How old are you?"', ['Uhlala kuphi?', 'Uneminyaka emingaki?', 'Unjani?'], 1),
                ],
                'homework': {
                    'title': 'Ngiyazethula (I introduce myself)',
                    'instructions': 'Prepare a short introduction to say in class.',
                    'tasks': [
                        'Write four isiZulu sentences: your name, age, grade and where you live.',
                        'Practise saying them aloud to someone at home until you can say them without reading.',
                    ],
                    'marks': 10,
                },
            },
            {
                'title': 'Umndeni wami: my family',
                'minutes': 40,
                'objectives': [
                    'I can name family members in isiZulu.',
                    'I can introduce a family member (Lo ngumama wami).',
                    'I can say how many brothers and sisters I have.',
                ],
                'notes': (
                    '<p><strong>Umndeni</strong> means family. <strong>Umndeni wami</strong> = my family.</p>'
                    '<ul><li><strong>umama</strong> = mother</li>'
                    '<li><strong>ubaba</strong> = father</li>'
                    '<li><strong>ugogo</strong> = grandmother</li>'
                    '<li><strong>umkhulu</strong> = grandfather</li>'
                    '<li><strong>umfowethu</strong> = my brother</li>'
                    '<li><strong>udadewethu</strong> = my sister</li>'
                    '<li><strong>ingane</strong> = child; <strong>izingane</strong> = children</li>'
                    '<li><strong>abazali</strong> = parents</li></ul>'
                    '<p>To introduce someone, say <strong>Lo ngu-</strong> ... <strong>wami</strong> (This is my ...):</p>'
                    '<ul><li><strong>Lo ngumama wami.</strong> = This is my mother.</li>'
                    '<li><strong>Lo ngubaba wami.</strong> = This is my father.</li>'
                    '<li><strong>Lo ngugogo wami.</strong> = This is my grandmother.</li></ul>'
                    '<p>To ask who someone is: <strong>Ngubani lo?</strong> = Who is this?</p>'
                    '<p>Talking about brothers and sisters:</p>'
                    '<ul><li><strong>Nginomfowethu oyedwa.</strong> = I have one brother.</li>'
                    '<li><strong>Nginodadewethu oyedwa.</strong> = I have one sister.</li></ul>'
                    '<p><strong>Ngiyawuthanda umndeni wami.</strong> = I love my family.</p>'
                ),
                'key_terms': [
                    ('umndeni', 'family'),
                    ('umama / ubaba', 'mother / father'),
                    ('ugogo / umkhulu', 'grandmother / grandfather'),
                    ('umfowethu / udadewethu', 'my brother / my sister'),
                    ('Ngubani lo?', 'Who is this?'),
                ],
                'example': {
                    'title': 'Class activity: Isithombe somndeni (A family picture)',
                    'html': (
                        '<p>Look at a drawing of a family. Your teacher points and asks:</p>'
                        '<p><strong>Thisha:</strong> Ngubani lo? <em>(Who is this?)</em><br>'
                        '<strong>Umfundi:</strong> Lo ngugogo. <em>(This is the grandmother.)</em><br>'
                        '<strong>Thisha:</strong> Kuhle kakhulu! Ngubani lo? <em>(Very good! Who is this?)</em><br>'
                        '<strong>Umfundi:</strong> Lo ngubaba. <em>(This is the father.)</em></p>'
                        '<p><strong>Your turn:</strong> Draw your own family. Point to each person and tell your partner: '
                        '"Lo ngumama wami", "Lo ngumfowethu" ...</p>'
                    ),
                },
                'video': {'id': '3SI6IS3qm7Y',
                          'title': '\U0001f3b6 Umndeni (Family) | Fun IsiZulu Song for Kids | Learn Family Members with Music! \U0001f3b6',
                          'channel': 'Mama Zulu', 'minutes': 2},
                'worksheet': {
                    'instructions': 'Match, translate and complete. Use the word list in the notes.',
                    'exercises': [
                        '1. Write the isiZulu word: mother, father, grandmother, grandfather',
                        '2. Write the English word: umfowethu, udadewethu, izingane, abazali',
                        '3. Complete: Lo ngu______ wami. (This is my father.)',
                        '4. Translate: Ngubani lo?',
                        '5. Translate into isiZulu: This is my grandmother.',
                        '6. Draw your family and write one isiZulu sentence about each person.',
                    ],
                },
                'quiz': [
                    ('mcq', 'What is "ugogo" in English?', ['mother', 'sister', 'grandfather', 'grandmother'], 3),
                    ('mcq', 'How do you say "This is my mother"?',
                     ['Lo ngumama wami.', 'Lo ngubaba wami.', 'Ngubani lo?', 'Umndeni wami.'], 0),
                    ('tf', '"Umndeni" means family.', True),
                    ('mcq', 'What does "Ngubani lo?" mean?', ['Where is it?', 'Who is this?', 'How are you?', 'How old are you?'], 1),
                ],
                'homework': {
                    'title': 'Umndeni wami',
                    'instructions': 'Make a small family poster.',
                    'tasks': [
                        'Draw or paste pictures of your family members.',
                        'Label each person in isiZulu (e.g. umama, ubaba, ugogo).',
                        'Write two sentences, e.g. "Lo ngumama wami."',
                    ],
                    'marks': 10,
                },
            },
        ],
    },

    # =====================================================================
    # GRADE 5 ISIZULU FIRST ADDITIONAL LANGUAGE
    # =====================================================================
    (5, 'ZUL-FAL'): {
        'topic': 'Ukubingelela, ukuzethula nomndeni: greetings, introductions and family',
        'caps': 'CAPS isiZulu FAL Gr 5 Term 1, Weeks 1-2: Ukulalela nokukhuluma (listening & speaking) - '
                'greetings and farewells, introducing yourself and others (ukuzethula), family (umndeni); '
                'dialogues; singular and plural greetings',
        'summary': 'Learners revise greetings and farewells (singular and plural), give a fuller introduction of '
                   'themselves including likes, and describe their family in short dialogues.',
        'days': [
            {
                'title': 'Ukubingelela nokuvalelisa: greetings and farewells',
                'minutes': 45,
                'objectives': [
                    'I can greet and say goodbye to one person and to a group.',
                    'I can choose the correct singular or plural form.',
                    'I can hold a short greeting conversation.',
                ],
                'notes': (
                    '<p>Let us revise and build on greetings. In isiZulu the greeting changes when you speak to '
                    '<strong>one</strong> person or to <strong>many</strong> people.</p>'
                    '<ul><li>Hello: <strong>Sawubona</strong> (one) / <strong>Sanibonani</strong> (many or an elder)</li>'
                    '<li>How are you?: <strong>Unjani?</strong> (one) / <strong>Ninjani?</strong> (many)</li>'
                    '<li>I am / we are well: <strong>Ngiyaphila</strong> / <strong>Siyaphila</strong></li>'
                    '<li>I am not well: <strong>Angiphili kahle</strong></li>'
                    '<li>Thank you: <strong>Ngiyabonga</strong> / <strong>Siyabonga</strong></li></ul>'
                    '<p><strong>Ukuvalelisa</strong> (saying goodbye):</p>'
                    '<ul><li>Stay well: <strong>Sala kahle</strong> (to one) / <strong>Salani kahle</strong> (to many) - said by the person leaving</li>'
                    '<li>Go well: <strong>Hamba kahle</strong> (to one) / <strong>Hambani kahle</strong> (to many) - said by the person staying</li>'
                    '<li><strong>Sizobonana</strong> = We will see each other (See you)</li>'
                    '<li><strong>Lala kahle</strong> = Sleep well (good night)</li></ul>'
                    '<p>Pattern: the plural forms often add <strong>-ni</strong>: sala, sala<strong>ni</strong>; hamba, hamba<strong>ni</strong>.</p>'
                ),
                'key_terms': [
                    ('ukubingelela', 'to greet'),
                    ('ukuvalelisa', 'to say goodbye'),
                    ('Ninjani?', 'How are you? (plural)'),
                    ('Salani kahle', 'Stay well (to many)'),
                    ('Sizobonana', 'See you / We will see each other'),
                ],
                'example': {
                    'title': 'Dialogue: Ekupheleni kosuku (At the end of the day)',
                    'html': (
                        '<p><strong>Ayanda:</strong> Sanibonani, Sipho noNomsa! Ninjani? <em>(Hello, Sipho and Nomsa! How are you?)</em><br>'
                        '<strong>Sipho noNomsa:</strong> Siyaphila, ngiyabonga. Wena unjani? <em>(We are well, thank you. And you?)</em><br>'
                        '<strong>Ayanda:</strong> Nami ngiyaphila. Sengiyahamba manje. Salani kahle! <em>(I am well too. I am going now. Stay well!)</em><br>'
                        '<strong>Sipho noNomsa:</strong> Hamba kahle, Ayanda! Sizobonana kusasa. <em>(Go well, Ayanda! See you tomorrow.)</em></p>'
                        '<p><strong>Activity:</strong> In groups of three, act out greeting and saying goodbye. Swap roles so that each '
                        'person is the one leaving once.</p>'
                    ),
                },
                'video': {'id': 'ggSd-FXDfDQ', 'title': 'Greetings & Farewells in isiZulu | Hello, Sawubona',
                          'channel': 'Polylingo Tunes', 'minutes': 2},
                'worksheet': {
                    'instructions': 'Write the correct isiZulu greeting or farewell for each situation.',
                    'exercises': [
                        '1. You greet your friend Lindo.',
                        '2. You greet your grandparents.',
                        '3. You ask your whole class how they are.',
                        '4. Your friends are leaving your house. What do you say to them?',
                        '5. You are leaving your aunt\'s house. What do you say to her?',
                        '6. Translate: Sizobonana kusasa.',
                        '7. Change to the plural: Sala kahle. Hamba kahle. Unjani?',
                    ],
                },
                'quiz': [
                    ('mcq', 'What is "How are you?" when you speak to many people?', ['Unjani?', 'Ninjani?', 'Sawubona', 'Siyaphila'], 1),
                    ('mcq', 'You are staying and your friends are leaving. What do you say?',
                     ['Salani kahle', 'Sala kahle', 'Hambani kahle', 'Sanibonani'], 2),
                    ('tf', '"Siyaphila" means "We are well".', True),
                    ('mcq', 'What does "Lala kahle" mean?', ['Sleep well', 'Go well', 'Thank you', 'I am sick'], 0),
                ],
                'homework': {
                    'title': 'Greeting cards',
                    'instructions': 'Make two small cards.',
                    'tasks': [
                        'On card 1, write a short isiZulu greeting conversation between two friends (4 lines).',
                        'On card 2, write how you say goodbye to your family in the morning in isiZulu, with English meanings.',
                    ],
                    'marks': 10,
                },
            },
            {
                'title': 'Ukuzethula: a fuller introduction',
                'minutes': 45,
                'objectives': [
                    'I can introduce myself with my name, age, grade, home and school.',
                    'I can say what I like (Ngithanda ...).',
                    'I can interview a classmate and introduce them to the class.',
                ],
                'notes': (
                    '<p>Last year you learnt to say your name. Now we give a <strong>fuller introduction</strong>.</p>'
                    '<ul><li><strong>Igama lami nguNomsa.</strong> = My name is Nomsa.</li>'
                    '<li><strong>Ngineminyaka eyishumi.</strong> = I am ten years old. '
                    '<strong>Ngineminyaka eyishumi nanye.</strong> = I am eleven years old.</li>'
                    '<li><strong>Ngifunda ibanga lesihlanu.</strong> = I am in Grade 5.</li>'
                    '<li><strong>Ngihlala ePitoli.</strong> = I live in Pretoria.</li>'
                    '<li><strong>Ngithanda ukudlala ibhola.</strong> = I like to play soccer.</li>'
                    '<li><strong>Ngithanda ukufunda.</strong> = I like to read.</li>'
                    '<li><strong>Angithandi ...</strong> = I do not like ...</li></ul>'
                    '<p>Questions to ask a classmate:</p>'
                    '<ul><li><strong>Ngubani igama lakho?</strong> = What is your name?</li>'
                    '<li><strong>Uneminyaka emingaki?</strong> = How old are you?</li>'
                    '<li><strong>Uhlala kuphi?</strong> = Where do you live?</li>'
                    '<li><strong>Uthanda ukwenzani?</strong> = What do you like to do?</li></ul>'
                    '<p>To introduce someone else: <strong>Lo nguSipho.</strong> = This is Sipho. '
                    '<strong>Uthanda ukucula.</strong> = He/She likes to sing.</p>'
                ),
                'key_terms': [
                    ('ukuzethula', 'to introduce yourself'),
                    ('Ngithanda ...', 'I like ...'),
                    ('Angithandi ...', 'I do not like ...'),
                    ('Uthanda ukwenzani?', 'What do you like to do?'),
                ],
                'example': {
                    'title': 'Interview and introduce',
                    'html': (
                        '<p><strong>Nomsa:</strong> Ngubani igama lakho? <em>(What is your name?)</em><br>'
                        '<strong>Sipho:</strong> Igama lami nguSipho. <em>(My name is Sipho.)</em><br>'
                        '<strong>Nomsa:</strong> Uneminyaka emingaki? <em>(How old are you?)</em><br>'
                        '<strong>Sipho:</strong> Ngineminyaka eyishumi nanye. <em>(I am eleven years old.)</em><br>'
                        '<strong>Nomsa:</strong> Uthanda ukwenzani? <em>(What do you like to do?)</em><br>'
                        '<strong>Sipho:</strong> Ngithanda ukudlala ibhola. <em>(I like to play soccer.)</em></p>'
                        '<p><strong>Nomsa tells the class:</strong> Lo nguSipho. Uneminyaka eyishumi nanye. Uthanda ukudlala ibhola. '
                        '<em>(This is Sipho. He is eleven years old. He likes to play soccer.)</em></p>'
                    ),
                },
                'video': {'id': 'ZJyCnTVKGmc',
                          'title': 'Learn isiZulu: How to Introduce Yourself Fully (Name, Siblings, Work, City, Study)',
                          'channel': 'Zulu Lessons with Thando', 'minutes': 6},
                'worksheet': {
                    'instructions': 'Answer the questions in isiZulu, then complete the translations.',
                    'exercises': [
                        '1. Ngubani igama lakho?',
                        '2. Uneminyaka emingaki?',
                        '3. Ufunda ibanga lesingaki?',
                        '4. Uhlala kuphi?',
                        '5. Uthanda ukwenzani?',
                        '6. Translate into English: Angithandi ukulala emini.',
                        '7. Write 5 sentences introducing a friend to the class. Start with "Lo ngu..."',
                    ],
                },
                'quiz': [
                    ('mcq', 'How do you say "I am in Grade 5"?',
                     ['Ngifunda ibanga lesine.', 'Ngifunda ibanga lesihlanu.', 'Ngineminyaka emihlanu.', 'Ngihlala ePitoli.'], 1),
                    ('mcq', 'What does "Ngithanda ukufunda" mean?', ['I like to read.', 'I like to sing.', 'I do not like school.', 'I live here.'], 0),
                    ('tf', '"Angithandi" means "I do not like".', True),
                    ('mcq', 'Which question asks "What do you like to do?"',
                     ['Uhlala kuphi?', 'Unjani?', 'Ngubani lo?', 'Uthanda ukwenzani?'], 3),
                ],
                'homework': {
                    'title': 'All about me',
                    'instructions': 'Make an "All about me" page in isiZulu.',
                    'tasks': [
                        'Write 6 sentences about yourself: name, age, grade, where you live, one thing you like and one thing you do not like.',
                        'Add a drawing of yourself doing what you like.',
                    ],
                    'marks': 12,
                },
            },
            {
                'title': 'Umndeni wami: talking about my family',
                'minutes': 45,
                'objectives': [
                    'I can name family members, including extended family.',
                    'I can say how many people are in my family.',
                    'I can describe my family in a short paragraph.',
                ],
                'notes': (
                    '<p><strong>Amalungu omndeni</strong> (family members):</p>'
                    '<ul><li><strong>umama / ubaba</strong> = mother / father; <strong>abazali</strong> = parents</li>'
                    '<li><strong>ugogo / umkhulu</strong> = grandmother / grandfather</li>'
                    '<li><strong>umfowethu / udadewethu</strong> = my brother / my sister</li>'
                    '<li><strong>ubhuti / usisi</strong> = older brother / older sister (also used to address them)</li>'
                    '<li><strong>umalume</strong> = uncle (mother\'s brother); <strong>umzala</strong> = cousin</li>'
                    '<li><strong>ingane / izingane</strong> = child / children</li></ul>'
                    '<p>Useful sentences:</p>'
                    '<ul><li><strong>Kunabantu abahlanu emndenini wami.</strong> = There are five people in my family.</li>'
                    '<li><strong>Nginomfowethu oyedwa nodadewethu oyedwa.</strong> = I have one brother and one sister.</li>'
                    '<li><strong>Ngihlala nogogo.</strong> = I live with my grandmother.</li>'
                    '<li><strong>Umama wami ungumhlengikazi.</strong> = My mother is a nurse.</li>'
                    '<li><strong>Ngiyawuthanda umndeni wami.</strong> = I love my family.</li></ul>'
                    '<p>Every family is different. Some children live with parents, some with grandparents or aunts. '
                    'Talk about <em>your</em> family in a way you are comfortable with.</p>'
                ),
                'key_terms': [
                    ('amalungu omndeni', 'family members'),
                    ('abazali', 'parents'),
                    ('umzala', 'cousin'),
                    ('umalume', 'uncle (mother\'s brother)'),
                    ('Ngihlala no...', 'I live with ...'),
                ],
                'example': {
                    'title': 'Reading: Umndeni kaLwandle (Lwandle\'s family)',
                    'html': (
                        '<p>Sawubona! Igama lami nguLwandle. Kunabantu abahlanu emndenini wami. Ngihlala nomama, nobaba, '
                        'nogogo nodadewethu omncane. Udadewethu nguAmahle. Ugogo uthanda ukupheka. Ngiyawuthanda umndeni wami.</p>'
                        '<p><em>Hello! My name is Lwandle. There are five people in my family. I live with my mother, my father, my '
                        'grandmother and my younger sister. My sister is Amahle. Grandmother likes to cook. I love my family.</em></p>'
                        '<p><strong>Questions:</strong> Bangaki abantu emndenini kaLwandle? <em>(How many people are in Lwandle\'s family?)</em> '
                        'Ngubani udadewabo? <em>(Who is his sister?)</em></p>'
                    ),
                },
                'video': {'id': '_VtrJERqQew', 'title': 'Family Members in isiZulu | Umndeni',
                          'channel': 'Polylingo Tunes', 'minutes': 2},
                'worksheet': {
                    'instructions': 'Read "Umndeni kaLwandle" again and answer. Then write about your own family.',
                    'exercises': [
                        '1. Bangaki abantu emndenini kaLwandle? (How many people?)',
                        '2. Ngubani udadewabo kaLwandle? (Who is his sister?)',
                        '3. Ugogo uthanda ukwenzani? (What does Grandmother like to do?)',
                        '4. Write the isiZulu word: parents, cousin, children, grandfather',
                        '5. Translate: I have one brother.',
                        '6. Write 5 isiZulu sentences about your family.',
                    ],
                },
                'quiz': [
                    ('mcq', 'What is "umzala" in English?', ['uncle', 'cousin', 'parent', 'child'], 1),
                    ('mcq', 'In the reading, what does Lwandle\'s grandmother like to do?',
                     ['to sing', 'to read', 'to cook', 'to play soccer'], 2),
                    ('tf', '"Abazali" means parents.', True),
                    ('mcq', 'How do you say "I live with my grandmother"?',
                     ['Ngihlala nogogo.', 'Ngiyabonga gogo.', 'Lo ngugogo.', 'Sala kahle gogo.'], 0),
                ],
                'homework': {
                    'title': 'Family tree',
                    'instructions': 'Draw a simple family tree.',
                    'tasks': [
                        'Draw a family tree with at least five people and label each one in isiZulu.',
                        'Write three sentences about your family, e.g. "Kunabantu abane emndenini wami."',
                    ],
                    'marks': 12,
                },
            },
        ],
    },

    # =====================================================================
    # GRADE 6 ISIZULU FIRST ADDITIONAL LANGUAGE
    # =====================================================================
    (6, 'ZUL-FAL'): {
        'topic': 'Ukuzethula, ulimi lasekilasini nomndeni: introductions, classroom language and family dialogues',
        'caps': 'CAPS isiZulu FAL Gr 6 Term 1, Weeks 1-2: Ukulalela nokukhuluma (listening & speaking) - '
                'greetings with respect, introducing yourself and others (ukuzethula), classroom instructions and '
                'requests, family (umndeni); dialogues; singular and plural forms',
        'summary': 'Learners use respectful greetings and full self-introductions, follow and give classroom instructions '
                   'in isiZulu, and talk about their families in a dialogue, noticing singular and plural forms.',
        'days': [
            {
                'title': 'Ukubingelela ngenhlonipho nokuzethula: respectful greetings and introductions',
                'minutes': 45,
                'objectives': [
                    'I can greet peers and elders correctly and respectfully.',
                    'I can introduce myself in a short speech (name, age, grade, home, likes).',
                    'I can introduce another person.',
                ],
                'notes': (
                    '<p><strong>Inhlonipho</strong> (respect) is central to isiZulu culture. When you greet an elder, use the plural '
                    'form even if it is one person: <strong>Sanibonani, Mama</strong> / <strong>Sanibonani, Baba</strong>. '
                    'Adults are often called <em>Mama</em> or <em>Baba</em> even if they are not your parents.</p>'
                    '<p><strong>Revision of greetings</strong>: Sawubona / Sanibonani; Unjani? / Ninjani?; Ngiyaphila / Siyaphila; '
                    'Ngiyabonga; Sala kahle / Hamba kahle.</p>'
                    '<p><strong>Ukuzethula</strong> (a short speech about yourself):</p>'
                    '<ul><li><strong>Igama lami nguKhanyisile.</strong> = My name is Khanyisile.</li>'
                    '<li><strong>Ngineminyaka eyishumi nambili.</strong> = I am twelve years old. '
                    '(eyishumi nanye = eleven)</li>'
                    '<li><strong>Ngifunda ibanga lesithupha.</strong> = I am in Grade 6.</li>'
                    '<li><strong>Ngihlala eThekwini.</strong> = I live in Durban.</li>'
                    '<li><strong>Ngithanda ukucula nokudansa.</strong> = I like singing and dancing.</li>'
                    '<li><strong>Ngifuna ukuba ngudokotela.</strong> = I want to be a doctor.</li></ul>'
                    '<p>To introduce someone: <strong>Ngicela ukwethula umngane wami, uSipho.</strong> = Please let me introduce my friend, Sipho.</p>'
                ),
                'key_terms': [
                    ('inhlonipho', 'respect'),
                    ('ukuzethula', 'to introduce yourself'),
                    ('ukwethula', 'to introduce (someone else)'),
                    ('umngane', 'friend'),
                    ('Ngifuna ukuba ngu...', 'I want to be a ...'),
                ],
                'example': {
                    'title': 'Model speech: Ngiyazethula',
                    'html': (
                        '<p>Sanibonani, thisha nabafundi. Igama lami nguKhanyisile. Ngineminyaka eyishumi nanye. '
                        'Ngifunda ibanga lesithupha. Ngihlala eThekwini nomama nogogo. Ngithanda ukufunda izincwadi nokudlala inetibhola. '
                        'Ngifuna ukuba nguthisha. Ngiyabonga.</p>'
                        '<p><em>Hello, teacher and learners. My name is Khanyisile. I am eleven years old. I am in Grade 6. I live in Durban '
                        'with my mother and grandmother. I like reading books and playing netball. I want to be a teacher. Thank you.</em></p>'
                        '<p><strong>Activity:</strong> Write your own speech of 6-7 sentences and present it to a group of four.</p>'
                    ),
                },
                'video': {'id': 'A6o5Mrrd4Ww', 'title': 'Learn isiZulu Greetings | How to Greet & Respond in Zulu for Beginners',
                          'channel': 'Zulu Lessons with Thando', 'minutes': 7},
                'worksheet': {
                    'instructions': 'Answer in isiZulu, then write your speech.',
                    'exercises': [
                        '1. How do you greet an elderly man respectfully?',
                        '2. Translate: I am twelve years old.',
                        '3. Translate: I am in Grade 6.',
                        '4. Translate: I want to be a doctor.',
                        '5. Introduce your friend in one sentence, starting "Ngicela ukwethula ..."',
                        '6. Write your own introduction speech (6-7 sentences).',
                    ],
                },
                'quiz': [
                    ('mcq', 'Which greeting is most respectful for one elderly woman?',
                     ['Sawubona', 'Sanibonani, Mama', 'Hamba kahle', 'Unjani'], 1),
                    ('mcq', 'What does "Ngifunda ibanga lesithupha" mean?',
                     ['I am in Grade 4.', 'I am in Grade 5.', 'I am in Grade 6.', 'I am six years old.'], 2),
                    ('tf', '"Inhlonipho" means respect.', True),
                    ('mcq', 'What does "umngane" mean?', ['friend', 'teacher', 'brother', 'school'], 0),
                ],
                'homework': {
                    'title': 'Prepare your speech',
                    'instructions': 'You will present your introduction in class.',
                    'tasks': [
                        'Finish your 6-7 sentence introduction speech in isiZulu.',
                        'Practise it aloud three times at home. Ask someone to listen and check that you greet respectfully at the start.',
                    ],
                    'marks': 10,
                },
            },
            {
                'title': 'Ulimi lasekilasini: classroom language',
                'minutes': 45,
                'objectives': [
                    'I can follow classroom instructions in isiZulu.',
                    'I can make polite requests using Ngicela ...',
                    'I can name common classroom objects.',
                ],
                'notes': (
                    '<p><strong>Imiyalelo yasekilasini</strong> (classroom instructions). Teachers usually speak to the whole class, '
                    'so the instructions end in <strong>-ni</strong> (plural):</p>'
                    '<ul><li><strong>Lalelani!</strong> = Listen!</li>'
                    '<li><strong>Thulani!</strong> = Be quiet!</li>'
                    '<li><strong>Sukumani.</strong> = Stand up. <strong>Hlalani phansi.</strong> = Sit down.</li>'
                    '<li><strong>Vulani izincwadi zenu.</strong> = Open your books. <strong>Valani izincwadi.</strong> = Close the books.</li>'
                    '<li><strong>Bhalani.</strong> = Write. <strong>Fundani.</strong> = Read.</li></ul>'
                    '<p>To one learner: <strong>Lalela, Sukuma, Hlala phansi, Bhala, Funda, Phendula</strong> (answer).</p>'
                    '<p><strong>Polite requests</strong> start with <strong>Ngicela</strong> (please may I / I ask for):</p>'
                    '<ul><li><strong>Ngicela ukuya ethoyilethi.</strong> = Please may I go to the toilet.</li>'
                    '<li><strong>Ngicela ipensele.</strong> = May I have a pencil, please.</li>'
                    '<li><strong>Ngicela uphinde.</strong> = Please repeat.</li>'
                    '<li><strong>Angiqondi.</strong> = I do not understand. <strong>Ngiyaxolisa.</strong> = I am sorry.</li></ul>'
                    '<p><strong>Izinto zasekilasini</strong>: incwadi (book), ipensele (pencil), irula (ruler), idesiki (desk), '
                    'isikhwama (bag), ibhodi (board), isikole (school), ikilasi (classroom).</p>'
                ),
                'key_terms': [
                    ('Ngicela ...', 'Please may I / May I have ...'),
                    ('Lalelani!', 'Listen! (plural)'),
                    ('Hlalani phansi', 'Sit down (plural)'),
                    ('Angiqondi', 'I do not understand'),
                    ('Ngiyaxolisa', 'I am sorry'),
                ],
                'example': {
                    'title': 'Dialogue: Ekilasini (In the classroom)',
                    'html': (
                        '<p><strong>Thisha:</strong> Sanibonani, bafundi. Hlalani phansi. Vulani izincwadi zenu. '
                        '<em>(Hello, learners. Sit down. Open your books.)</em><br>'
                        '<strong>Bongani:</strong> Ngiyaxolisa, thisha. Angiqondi. Ngicela uphinde. '
                        '<em>(Sorry, teacher. I do not understand. Please repeat.)</em><br>'
                        '<strong>Thisha:</strong> Vulani izincwadi zenu ekhasini lesihlanu. <em>(Open your books on page five.)</em><br>'
                        '<strong>Bongani:</strong> Ngiyabonga, thisha. Ngicela irula. <em>(Thank you, teacher. May I have a ruler, please.)</em><br>'
                        '<strong>Thisha:</strong> Nanti. <em>(Here it is.)</em></p>'
                        '<p><strong>Game - "Uthisha uthi" (Teacher says):</strong> follow the instruction only when the leader starts with '
                        '"Uthisha uthi ...", e.g. "Uthisha uthi sukumani!"</p>'
                    ),
                },
                'video': {'id': '8vd2IhJfpQA', 'title': 'Let’s Learn About School in isiZulu | Easy Zulu Words for Beginners',
                          'channel': 'ZuluMama', 'minutes': 7},
                'worksheet': {
                    'instructions': 'Write the isiZulu or English meaning.',
                    'exercises': [
                        '1. English meaning: Vulani izincwadi zenu.',
                        '2. English meaning: Thulani!',
                        '3. isiZulu for: Sit down (to the class).',
                        '4. isiZulu for: Please may I go to the toilet.',
                        '5. isiZulu for: I do not understand.',
                        '6. Name in isiZulu: book, pencil, ruler, bag, desk',
                        '7. Change to the plural instruction: Sukuma. Lalela. Bhala.',
                    ],
                },
                'quiz': [
                    ('mcq', 'What does "Lalelani!" mean?', ['Sit down!', 'Write!', 'Listen!', 'Stand up!'], 2),
                    ('mcq', 'How do you politely ask for a pencil?',
                     ['Ngicela ipensele.', 'Vulani ipensele.', 'Angiqondi ipensele.', 'Hamba ipensele.'], 0),
                    ('tf', '"Angiqondi" means "I understand".', False),
                    ('mcq', 'What is "isikhwama"?', ['desk', 'bag', 'board', 'ruler'], 1),
                ],
                'homework': {
                    'title': 'Classroom labels',
                    'instructions': 'Make labels for things at home or in your school bag.',
                    'tasks': [
                        'Make 6 labels in isiZulu for classroom objects (e.g. ipensele, irula) and stick them on the real objects.',
                        'Write five classroom instructions in isiZulu with their English meanings.',
                    ],
                    'marks': 12,
                },
            },
            {
                'title': 'Umndeni wami: family dialogue and plurals',
                'minutes': 45,
                'objectives': [
                    'I can describe my family and ask others about theirs.',
                    'I can form plurals of family nouns (umama / omama; umfundi / abafundi).',
                    'I can take part in a short family dialogue.',
                ],
                'notes': (
                    '<p><strong>Family words</strong>: umama, ubaba, ugogo, umkhulu, umfowethu, udadewethu, umzala (cousin), '
                    'umalume (uncle, mother\'s brother), abazali (parents), izingane (children).</p>'
                    '<p><strong>Singular and plural (inani)</strong>: isiZulu nouns belong to noun classes. Two common patterns:</p>'
                    '<ul><li><strong>u- becomes o-</strong>: umama / <strong>o</strong>mama, ubaba / <strong>o</strong>baba, '
                    'ugogo / <strong>o</strong>gogo, uthisha / <strong>o</strong>thisha</li>'
                    '<li><strong>um- becomes aba-</strong>: umfundi / <strong>aba</strong>fundi (learner / learners), '
                    'umngane / <strong>aba</strong>ngane (friend / friends), umzali / <strong>aba</strong>zali (parent / parents)</li></ul>'
                    '<p><strong>Asking about family</strong></p>'
                    '<ul><li><strong>Bangaki abantu emndenini wakho?</strong> = How many people are in your family?</li>'
                    '<li><strong>Unabafowenu nodadewenu?</strong> = Do you have brothers and sisters?</li>'
                    '<li><strong>Uhlala nobani?</strong> = Who do you live with?</li></ul>'
                    '<p>Answers: <strong>Kunabantu abane.</strong> = There are four people. '
                    '<strong>Nginabafowethu ababili.</strong> = I have two brothers. '
                    '<strong>Ngihlala nomama nogogo.</strong> = I live with my mother and grandmother.</p>'
                ),
                'key_terms': [
                    ('inani', 'number (singular / plural)'),
                    ('omama', 'mothers (plural of umama)'),
                    ('abafundi', 'learners (plural of umfundi)'),
                    ('Uhlala nobani?', 'Who do you live with?'),
                    ('Bangaki ...?', 'How many (people) ...?'),
                ],
                'example': {
                    'title': 'Dialogue: Umndeni wakho unjani? (What is your family like?)',
                    'html': (
                        '<p><strong>Lerato:</strong> Bangaki abantu emndenini wakho, Musa? <em>(How many people are in your family, Musa?)</em><br>'
                        '<strong>Musa:</strong> Kunabantu abayisithupha. <em>(There are six people.)</em><br>'
                        '<strong>Lerato:</strong> Uhlala nobani? <em>(Who do you live with?)</em><br>'
                        '<strong>Musa:</strong> Ngihlala nabazali bami, nogogo, nomkhulu nodadewethu. <em>(I live with my parents, my grandmother, '
                        'my grandfather and my sister.)</em><br>'
                        '<strong>Lerato:</strong> Unabafowenu? <em>(Do you have brothers?)</em><br>'
                        '<strong>Musa:</strong> Cha, anginabo. Wena? <em>(No, I do not have any. And you?)</em><br>'
                        '<strong>Lerato:</strong> Nginomfowethu oyedwa. <em>(I have one brother.)</em></p>'
                        '<p><strong>Activity:</strong> Practise the dialogue, then change it to talk about your own families.</p>'
                    ),
                },
                'video': {'id': 'tF7sK9NtF0I', 'title': 'Umndeni Wami-My Family in IsiZulu', 'channel': 'Nuances', 'minutes': 6},
                'worksheet': {
                    'instructions': 'Complete the exercises in isiZulu.',
                    'exercises': [
                        '1. Write the plural: umama, ugogo, uthisha',
                        '2. Write the plural: umfundi, umngane, umzali',
                        '3. Translate: How many people are in your family?',
                        '4. Translate: I live with my mother and my grandmother.',
                        '5. Answer in isiZulu: Uhlala nobani?',
                        '6. Write a 6-line dialogue between you and a friend about your families.',
                    ],
                },
                'quiz': [
                    ('mcq', 'What is the plural of "umfundi"?', ['omfundi', 'imifundi', 'abafundi', 'izifundi'], 2),
                    ('mcq', 'What is the plural of "ugogo"?', ['abagogo', 'ogogo', 'izigogo', 'amagogo'], 1),
                    ('tf', '"Uhlala nobani?" means "Who do you live with?"', True),
                    ('mcq', 'How do you say "I have one brother"?',
                     ['Nginomfowethu oyedwa.', 'Nginodadewethu oyedwa.', 'Ngihlala nobaba.', 'Kunabantu abane.'], 0),
                ],
                'homework': {
                    'title': 'Family interview',
                    'instructions': 'Interview someone at home or a friend in isiZulu (or practise with a family member).',
                    'tasks': [
                        'Ask three questions about their family (Bangaki abantu ...? Uhlala nobani? Unabafowenu?) and write their answers.',
                        'Write a paragraph of 5 sentences about your own family.',
                        'List 4 family nouns with their plurals.',
                    ],
                    'marks': 15,
                },
            },
        ],
    },
}
