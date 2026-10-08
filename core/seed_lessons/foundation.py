"""Foundation Phase (Grades 1-3) — Term 1, Week 1 demo lessons.

Offerings (15): grades 1, 2, 3 x
    ENG-HL   English Home Language
    ZUL-FAL  isiZulu First Additional Language
    MATH     Mathematics
    LIFE-SK  Life Skills (Beginning Knowledge, Personal and Social Well-being,
             Creative Arts, Physical Education)
    CODING   Coding and Robotics

CAPS sources used:
    - CAPS Foundation Phase Mathematics Gr 1-3 (DBE 2011) and the DBE Annual Teaching
      Plans, Term 1 (Numbers, operations and relationships: counting, number symbols and
      names, place value; Gr 1 to 10/20, Gr 2 to 100, Gr 3 to 1000).
    - CAPS Foundation Phase English Home Language Gr 1-3 and ATP Term 1 (Listening and
      Speaking, Phonics, Reading, Handwriting, Writing).
    - CAPS Foundation Phase First Additional Language Gr 1-3 (isiZulu) and ATP Term 1
      (Listening and Speaking: greetings, classroom instructions, vocabulary themes).
    - CAPS Foundation Phase Life Skills Gr 1-3 and ATP Term 1 (Beginning Knowledge and
      Personal and Social Well-being: Me / My school / My body / Healthy habits;
      Creative Arts; Physical Education).
    - DBE draft CAPS Coding and Robotics Gr R-3 (Pattern recognition, Algorithms and
      Coding: sequencing, unplugged coding, giving and following instructions).
"""

LESSONS = {

    # ------------------------------------------------------------------ MATHEMATICS
    (1, 'MATH'): {
        'topic': 'Counting and number recognition to 10',
        'caps': 'Numbers, Operations and Relationships: count objects; count forwards and '
                'backwards in ones; know number symbols and number names 1-10 (Gr 1 Term 1 ATP)',
        'summary': 'Learners count real objects to 10, read and write the number symbols 1 to 10, '
                   'and count forwards and backwards, finding one more and one less.',
        'days': [
            {
                'title': 'Counting objects to 10',
                'minutes': 30,
                'objectives': [
                    'I can count objects one by one up to 10.',
                    'I can touch each object once as I count.',
                    'I can say how many there are.',
                ],
                'notes': (
                    '<p>Today we <strong>count</strong> things.</p>'
                    '<ul><li>Touch one thing.</li><li>Say one number.</li>'
                    '<li>Move it to the side.</li></ul>'
                    '<p>The <strong>last number</strong> you say tells you <em>how many</em>.</p>'
                    '<p>Count your fingers: 1, 2, 3, 4, 5, 6, 7, 8, 9, 10. You have 10 fingers!</p>'
                ),
                'key_terms': [('count', 'say the numbers in order, one for each thing'),
                              ('how many', 'the total number of things')],
                'example': {'title': 'Class activity: count the bottle tops', 'html': (
                    '<p>The teacher puts 7 bottle tops on the mat.</p>'
                    '<ol><li>Point to each top and count: 1, 2, 3, 4, 5, 6, 7.</li>'
                    '<li>Move each top to the side after you count it.</li>'
                    '<li>The last number was 7. There are <strong>7</strong> bottle tops.</li></ol>'
                    '<p>Now count again with a friend. Do you get the same number?</p>')},
                'video': {'id': 'k4i6fu0bTQ8', 'title': '@Numberblocks- Count to Ten | Learn to Count',
                          'channel': 'Numberblocks', 'minutes': 4},
                'worksheet': {'instructions': 'Count the things. Write how many.',
                              'exercises': [
                                  'Count the stars: * * *   = ____',
                                  'Count the stars: * * * * * *   = ____',
                                  'Count the circles: o o o o o   = ____',
                                  'Count the circles: o o o o o o o o   = ____',
                                  'Count the hearts you draw: draw 4 hearts.',
                                  'Count the windows in your classroom = ____',
                              ]},
                'quiz': [
                    ('mcq', 'How many stars? * * * *', ['3', '4', '5'], 1),
                    ('mcq', 'How many fingers on one hand?', ['5', '10', '4'], 0),
                    ('tf', 'The last number you say tells you how many.', True),
                    ('mcq', 'How many circles? o o o o o o', ['5', '7', '6'], 2),
                ],
                'homework': {'title': 'Count at home',
                             'instructions': 'Count things at home with a grown-up.',
                             'tasks': ['Count the spoons in the drawer.',
                                       'Count the chairs at home.',
                                       'Count the shoes by the door. Tell your grown-up how many.'],
                             'marks': 5},
            },
            {
                'title': 'Number symbols 1 to 10',
                'minutes': 30,
                'objectives': [
                    'I can read the numbers 1 to 10.',
                    'I can write the numbers 1 to 10.',
                    'I can match a number to a group of objects.',
                ],
                'notes': (
                    '<p>A <strong>number symbol</strong> is how we write a number.</p>'
                    '<p>1 2 3 4 5 6 7 8 9 10</p>'
                    '<ul><li>Start at the top when you write.</li>'
                    '<li>10 has two parts: a 1 and a 0.</li></ul>'
                    '<p>Draw the number in the air. Then draw it on the mat with your finger.</p>'
                ),
                'key_terms': [('number symbol', 'the way we write a number, like 3')],
                'example': {'title': 'Class activity: match the number', 'html': (
                    '<p>The teacher holds up a card with <strong>5</strong>.</p>'
                    '<ol><li>Read it: "five".</li><li>Show 5 fingers.</li>'
                    '<li>Put 5 blocks next to the card.</li></ol>'
                    '<p>Now try with 3, 8 and 10.</p>')},
                'video': {'id': 'pzmB0GoEKkA',
                          'title': "Let's Learn Our Numbers 0-10 | Counting Song for Kids | Jack Hartmann Writing Numbers",
                          'channel': 'Jack Hartmann Kids Music Channel', 'minutes': 4},
                'worksheet': {'instructions': 'Trace and write the numbers. Draw dots to match.',
                              'exercises': [
                                  'Write the numbers 1 to 5: ___ ___ ___ ___ ___',
                                  'Write the numbers 6 to 10: ___ ___ ___ ___ ___',
                                  'Draw 3 dots next to the number 3.',
                                  'Draw 6 dots next to the number 6.',
                                  'Draw 9 dots next to the number 9.',
                                  'Circle the number 7:  4  7  1',
                              ]},
                'quiz': [
                    ('mcq', 'Which number is eight?', ['6', '3', '8'], 2),
                    ('mcq', 'How many dots? . . .', ['3', '2', '4'], 0),
                    ('tf', 'The number 10 is written with a 1 and a 0.', True),
                    ('mcq', 'Which number comes after 4?', ['3', '5', '6'], 1),
                ],
                'homework': {'title': 'Find numbers at home',
                             'instructions': 'Look for numbers at home with a grown-up.',
                             'tasks': ['Find 3 numbers on a clock, phone or calendar. Read them.',
                                       'Write the numbers 1 to 10 on paper.',
                                       'Draw 5 balls and write 5 next to them.'],
                             'marks': 10},
            },
            {
                'title': 'Count forwards and backwards; one more and one less',
                'minutes': 30,
                'objectives': [
                    'I can count forwards from 1 to 10.',
                    'I can count backwards from 10 to 1.',
                    'I can say one more and one less than a number.',
                ],
                'notes': (
                    '<p>Count <strong>forwards</strong>: 1, 2, 3, 4, 5, 6, 7, 8, 9, 10.</p>'
                    '<p>Count <strong>backwards</strong>: 10, 9, 8, 7, 6, 5, 4, 3, 2, 1. Blast off!</p>'
                    '<ul><li><strong>One more</strong> is the next number. One more than 4 is 5.</li>'
                    '<li><strong>One less</strong> is the number before. One less than 4 is 3.</li></ul>'
                ),
                'key_terms': [('one more', 'the next number when you count forwards'),
                              ('one less', 'the number just before')],
                'example': {'title': 'Class activity: the number line jump', 'html': (
                    '<p>Put cards 1 to 10 on the floor in a line.</p>'
                    '<ol><li>A child stands on 6.</li><li>"Jump one more!" The child jumps to 7.</li>'
                    '<li>"Jump one less!" The child jumps back to 6, then to 5.</li></ol>'
                    '<p>One more than 6 is 7. One less than 6 is 5.</p>')},
                'video': {'id': 'mb5n2o-NWSQ', 'title': 'Counting to 10 Forward and Backward | Jack Hartmann',
                          'channel': 'Jack Hartmann Kids Music Channel', 'minutes': 3},
                'worksheet': {'instructions': 'Fill in the missing numbers.',
                              'exercises': [
                                  '1, 2, ___, 4, ___, 6',
                                  '5, 6, 7, ___, ___, 10',
                                  '10, 9, ___, 7, ___, 5',
                                  'One more than 3 is ___',
                                  'One less than 8 is ___',
                                  'One more than 9 is ___',
                              ]},
                'quiz': [
                    ('mcq', 'One more than 5 is ...', ['4', '6', '7'], 1),
                    ('mcq', 'One less than 3 is ...', ['2', '4', '1'], 0),
                    ('mcq', 'What comes next? 10, 9, 8, ...', ['9', '6', '7'], 2),
                    ('tf', 'When we count backwards, the numbers get smaller.', True),
                ],
                'homework': {'title': 'Blast off!',
                             'instructions': 'Play a counting game with a grown-up.',
                             'tasks': ['Count backwards from 10 to 1 and jump up on "blast off".',
                                       'Your grown-up says a number. You say one more.',
                                       'Your grown-up says a number. You say one less.'],
                             'marks': 5},
            },
        ],
    },

    (2, 'MATH'): {
        'topic': 'Count, order and name numbers to 100',
        'caps': 'Numbers, Operations and Relationships: count forwards and backwards in 1s, 2s, '
                '5s and 10s; know number symbols and number names; order numbers to 100 '
                '(Gr 2 Term 1 ATP)',
        'summary': 'Learners count to 100 on a hundred chart, skip count in 2s, 5s and 10s, '
                   'and read and write number names.',
        'days': [
            {
                'title': 'Counting to 100 on the hundred chart',
                'minutes': 35,
                'objectives': [
                    'I can count forwards and backwards in 1s up to 100.',
                    'I can find numbers on a hundred chart.',
                    'I can say the number before and after.',
                ],
                'notes': (
                    '<p>A <strong>hundred chart</strong> has 10 rows of 10 numbers.</p>'
                    '<ul><li>Move right: the number gets 1 bigger.</li>'
                    '<li>Move down: the number gets 10 bigger.</li></ul>'
                    '<p>Look at 37. The number <strong>before</strong> is 36. '
                    'The number <strong>after</strong> is 38.</p>'
                    '<p>After 39 comes 40. After 99 comes 100.</p>'
                ),
                'key_terms': [('hundred chart', 'a grid of the numbers 1 to 100'),
                              ('before / after', 'the number just smaller / just bigger')],
                'example': {'title': 'Worked example: before and after', 'html': (
                    '<p>Find 59 on the chart.</p>'
                    '<ol><li>One step left is <strong>58</strong> (before).</li>'
                    '<li>One step right is <strong>60</strong> (after).</li>'
                    '<li>Count on: 59, 60, 61, 62.</li><li>Count back: 59, 58, 57, 56.</li></ol>')},
                'video': {'id': '0TgLtF3PMOc',
                          'title': "Let's Get Fit | Count to 100 by 1's | 100 Days of School Song | Counting to 100 | Jack Hartmann",
                          'channel': 'Jack Hartmann Kids Music Channel', 'minutes': 6},
                'worksheet': {'instructions': 'Fill in the missing numbers.',
                              'exercises': [
                                  '23, 24, ___, ___, 27, 28',
                                  '48, 49, ___, 51, ___',
                                  '71, 70, ___, 68, ___',
                                  'Before 40 is ___. After 40 is ___.',
                                  'Before 86 is ___. After 86 is ___.',
                                  '96, 97, ___, ___, 100',
                              ]},
                'quiz': [
                    ('mcq', 'What number comes after 49?', ['48', '50', '59'], 1),
                    ('mcq', 'What number comes before 70?', ['69', '71', '60'], 0),
                    ('tf', 'On a hundred chart, moving down one row adds 10.', True),
                    ('mcq', 'What comes next? 97, 98, 99, ...', ['90', '98', '100'], 2),
                ],
                'homework': {'title': 'My counting chart',
                             'instructions': 'Practise counting with a grown-up.',
                             'tasks': ['Count from 1 to 100 out loud.',
                                       'Count backwards from 30 to 1.',
                                       'Write the numbers from 41 to 60.'],
                             'marks': 10},
            },
            {
                'title': 'Skip counting in 2s, 5s and 10s',
                'minutes': 35,
                'objectives': [
                    'I can count in 2s to 20.',
                    'I can count in 5s and 10s to 100.',
                    'I can find the pattern on the hundred chart.',
                ],
                'notes': (
                    '<p>When we <strong>skip count</strong>, we jump over numbers.</p>'
                    '<ul><li>In 2s: 2, 4, 6, 8, 10, 12 ...</li>'
                    '<li>In 5s: 5, 10, 15, 20, 25 ... Numbers end in 5 or 0.</li>'
                    '<li>In 10s: 10, 20, 30, 40 ... Numbers end in 0.</li></ul>'
                    '<p>Skip counting is faster than counting in 1s.</p>'
                ),
                'key_terms': [('skip count', 'count in jumps of the same size')],
                'example': {'title': 'Worked example: counting shoes in 2s', 'html': (
                    '<p>6 children stand in a line. How many shoes?</p>'
                    '<p>Each child has 2 shoes. Count in 2s: 2, 4, 6, 8, 10, <strong>12</strong>.</p>'
                    '<p>There are 12 shoes. Now count 4 hands in 5s: 5, 10, 15, <strong>20</strong> fingers.</p>')},
                'video': {'id': 'q_yUC1NCFkE',
                          'title': "Workout & Count | Skip Count by 2's, 5's and 10's | Count Backwards | Jack Hartmann",
                          'channel': 'Jack Hartmann Kids Music Channel', 'minutes': 5},
                'worksheet': {'instructions': 'Skip count. Fill in the gaps.',
                              'exercises': [
                                  'Count in 2s: 2, 4, ___, 8, ___, 12',
                                  'Count in 5s: 5, 10, ___, 20, ___, 30',
                                  'Count in 10s: 10, 20, ___, ___, 50',
                                  'Count in 10s: 60, 70, ___, ___, 100',
                                  'Count in 2s: 14, 16, ___, 20',
                                  'How many eyes do 5 children have? Count in 2s: ___',
                              ]},
                'quiz': [
                    ('mcq', 'Count in 5s: 5, 10, 15, ...', ['16', '20', '25'], 1),
                    ('mcq', 'Count in 10s: 30, 40, 50, ...', ['60', '51', '55'], 0),
                    ('mcq', 'Count in 2s: 6, 8, 10, ...', ['11', '14', '12'], 2),
                    ('tf', 'When we count in 10s, every number ends in 0.', True),
                ],
                'homework': {'title': 'Skip count at home',
                             'instructions': 'Use things at home to skip count.',
                             'tasks': ['Count socks in pairs: count in 2s.',
                                       'Count to 50 in 5s while clapping.',
                                       'Count to 100 in 10s and write the numbers.'],
                             'marks': 10},
            },
            {
                'title': 'Number names and ordering numbers',
                'minutes': 35,
                'objectives': [
                    'I can read and write number names to twenty and the tens to one hundred.',
                    'I can order numbers from smallest to biggest.',
                ],
                'notes': (
                    '<p>A <strong>number name</strong> is the number written in words.</p>'
                    '<ul><li>1 one, 2 two, 3 three, 4 four, 5 five</li>'
                    '<li>6 six, 7 seven, 8 eight, 9 nine, 10 ten</li>'
                    '<li>20 twenty, 30 thirty, 40 forty, 50 fifty</li></ul>'
                    '<p>We write 34 as <em>thirty-four</em>.</p>'
                    '<p>To <strong>order</strong> numbers, look at the tens first. 23 is smaller than 32.</p>'
                ),
                'key_terms': [('number name', 'a number written in words'),
                              ('order', 'put numbers from smallest to biggest, or biggest to smallest')],
                'example': {'title': 'Worked example: ordering numbers', 'html': (
                    '<p>Put in order, smallest first: 45, 17, 60, 38.</p>'
                    '<ol><li>Look at the tens: 4, 1, 6, 3.</li>'
                    '<li>Smallest tens first: 17, 38, 45, 60.</li></ol>'
                    '<p>Answer: <strong>17, 38, 45, 60</strong>.</p>')},
                'video': {'id': 'CRQdhS1TJdo', 'title': 'Number Words | 1-100 | Jack Hartmann',
                          'channel': 'Jack Hartmann Kids Music Channel', 'minutes': 5},
                'worksheet': {'instructions': 'Write the number names. Order the numbers.',
                              'exercises': [
                                  'Write in words: 7 = __________',
                                  'Write in words: 12 = __________',
                                  'Write in words: 40 = __________',
                                  'Write the number: twenty-six = ____',
                                  'Order, smallest first: 52, 25, 39 = ____, ____, ____',
                                  'Order, biggest first: 18, 81, 60 = ____, ____, ____',
                              ]},
                'quiz': [
                    ('mcq', 'Which word is 30?', ['thirteen', 'three', 'thirty'], 2),
                    ('mcq', 'Which number is the biggest?', ['61', '16', '60'], 0),
                    ('tf', '"Fifteen" is the number name for 50.', False),
                    ('mcq', 'Which list goes from smallest to biggest?',
                     ['30, 20, 10', '12, 21, 35', '50, 15, 5'], 1),
                ],
                'homework': {'title': 'Number names',
                             'instructions': 'Practise number names with a grown-up.',
                             'tasks': ['Write the number names from one to ten.',
                                       'Write the ages of 3 people at home in numbers and words.',
                                       'Put the ages in order from youngest to oldest.'],
                             'marks': 10},
            },
        ],
    },

    (3, 'MATH'): {
        'topic': 'Numbers to 1000 and place value',
        'caps': 'Numbers, Operations and Relationships: count forwards and backwards in 10s and '
                '100s; number symbols and names to 1000; place value of 3-digit numbers '
                '(hundreds, tens, units); compare and order numbers to 1000 (Gr 3 Term 1 ATP)',
        'summary': 'Learners count in 10s and 100s to 1000, break 3-digit numbers into hundreds, '
                   'tens and units, and compare and order numbers to 1000.',
        'days': [
            {
                'title': 'Counting in 10s and 100s to 1000',
                'minutes': 40,
                'objectives': [
                    'I can count forwards and backwards in 100s to 1000.',
                    'I can count in 10s from any number.',
                    'I can read and write 3-digit numbers.',
                ],
                'notes': (
                    '<p>We can count in <strong>hundreds</strong>: 100, 200, 300 ... 900, 1000.</p>'
                    '<p>We can count in <strong>tens</strong> from any number: 240, 250, 260, 270.</p>'
                    '<ul><li>When counting in 10s, the tens digit changes.</li>'
                    '<li>When counting in 100s, the hundreds digit changes.</li></ul>'
                    '<p>After 390, counting in 10s, comes 400.</p>'
                    '<p>Ten hundreds make one thousand (1000).</p>'
                ),
                'key_terms': [('hundred', '10 tens, written 100'),
                              ('thousand', '10 hundreds, written 1000')],
                'example': {'title': 'Worked example: count on in 10s', 'html': (
                    '<p>Count on in 10s from 365, five times.</p>'
                    '<p>365, 375, 385, 395, <strong>405</strong>, 415.</p>'
                    '<p>Watch out: after 395 comes 405, because 10 tens make a new hundred.</p>')},
                'video': {'id': 'l3R6wdHs9n8',
                          'title': 'The Counting by Hundreds Song | Counting Songs | Scratch Garden',
                          'channel': 'Scratch Garden', 'minutes': 3},
                'worksheet': {'instructions': 'Count on or back. Fill in the gaps.',
                              'exercises': [
                                  'Count in 100s: 100, 200, ___, ___, 500',
                                  'Count in 100s: 1000, 900, ___, ___, 600',
                                  'Count in 10s: 230, 240, ___, ___, 270',
                                  'Count in 10s: 580, 590, ___, ___',
                                  'Count in 10s: 714, 724, ___, ___',
                                  'Count back in 10s: 450, 440, ___, ___',
                              ]},
                'quiz': [
                    ('mcq', 'Count in 100s: 400, 500, 600, ...', ['610', '700', '601'], 1),
                    ('mcq', 'Count in 10s: 290, 300, ...', ['310', '400', '301'], 0),
                    ('tf', 'Ten hundreds make one thousand.', True),
                    ('mcq', 'Count back in 10s: 520, 510, ...', ['509', '410', '500'], 2),
                ],
                'homework': {'title': 'Counting to 1000',
                             'instructions': 'Practise with a grown-up listening.',
                             'tasks': ['Count from 100 to 1000 in 100s, then back again.',
                                       'Count in 10s from 650 to 750 and write the numbers.',
                                       'Find a 3-digit number at home (price, page number). Read it aloud.'],
                             'marks': 10},
            },
            {
                'title': 'Place value: hundreds, tens and units',
                'minutes': 40,
                'objectives': [
                    'I can say the value of each digit in a 3-digit number.',
                    'I can break up a number into hundreds, tens and units.',
                    'I can build a number from its parts.',
                ],
                'notes': (
                    '<p>Every digit has a <strong>place</strong> and a <strong>value</strong>.</p>'
                    '<p>Look at <strong>346</strong>:</p>'
                    '<ul><li>3 is in the hundreds place. Its value is 300.</li>'
                    '<li>4 is in the tens place. Its value is 40.</li>'
                    '<li>6 is in the units place. Its value is 6.</li></ul>'
                    '<p>346 = 300 + 40 + 6. This is called <em>expanded notation</em>.</p>'
                    '<p>A 0 holds a place: in 507 there are no tens.</p>'
                ),
                'key_terms': [('digit', 'one of the symbols 0 to 9'),
                              ('place value', 'what a digit is worth because of its place'),
                              ('units', 'ones')],
                'example': {'title': 'Worked example: break up and build up', 'html': (
                    '<p>Break up 728: 7 hundreds, 2 tens, 8 units. 728 = 700 + 20 + 8.</p>'
                    '<p>Build up: 600 + 5 = <strong>605</strong> (6 hundreds, 0 tens, 5 units).</p>'
                    '<p>Use flard cards: put the 8 on the 20 and the 20 on the 700 to show 728.</p>')},
                'video': {'id': 'a4FXl4zb3E4',
                          'title': 'Place Value Song For Kids | Ones, Tens, & Hundreds | 1st - 3rd Grade',
                          'channel': 'Numberock', 'minutes': 4},
                'worksheet': {'instructions': 'Answer the place value questions.',
                              'exercises': [
                                  '254 = ___ hundreds ___ tens ___ units',
                                  '691 = ___ + ___ + ___',
                                  '400 + 30 + 2 = ___',
                                  '800 + 9 = ___',
                                  'What is the value of the 7 in 372? ___',
                                  'What is the value of the 5 in 518? ___',
                              ]},
                'quiz': [
                    ('mcq', 'What is the value of 4 in 248?', ['4', '400', '40'], 2),
                    ('mcq', '500 + 60 + 3 = ?', ['563', '536', '5603'], 0),
                    ('tf', 'In 307 there are no tens.', True),
                    ('mcq', 'How many hundreds in 915?', ['1', '9', '5'], 1),
                ],
                'homework': {'title': 'Place value detective',
                             'instructions': 'Use numbers you find at home.',
                             'tasks': ['Write 3 numbers between 100 and 999 that you find at home.',
                                       'Break up each number into hundreds, tens and units.',
                                       'Ask a grown-up to say a number; write it in expanded notation.'],
                             'marks': 12},
            },
            {
                'title': 'Comparing and ordering numbers to 1000',
                'minutes': 40,
                'objectives': [
                    'I can compare two 3-digit numbers.',
                    'I can use the words bigger than, smaller than and equal to.',
                    'I can order numbers from smallest to biggest.',
                ],
                'notes': (
                    '<p>To <strong>compare</strong> numbers, start with the biggest place.</p>'
                    '<ol><li>Compare the hundreds.</li><li>If they are the same, compare the tens.</li>'
                    '<li>If the tens are also the same, compare the units.</li></ol>'
                    '<p>We use signs: <strong>&gt;</strong> means bigger than, '
                    '<strong>&lt;</strong> means smaller than, <strong>=</strong> means equal to.</p>'
                    '<p>Example: 462 &gt; 426 because 6 tens is more than 2 tens.</p>'
                ),
                'key_terms': [('compare', 'decide which number is bigger or smaller'),
                              ('ascending order', 'from smallest to biggest')],
                'example': {'title': 'Worked example: order four numbers', 'html': (
                    '<p>Order from smallest to biggest: 731, 317, 713, 371.</p>'
                    '<ol><li>Hundreds: 317 and 371 have 3 hundreds; 731 and 713 have 7 hundreds.</li>'
                    '<li>317 &lt; 371 (1 ten is less than 7 tens).</li>'
                    '<li>713 &lt; 731 (1 ten is less than 3 tens).</li></ol>'
                    '<p>Answer: <strong>317, 371, 713, 731</strong>.</p>')},
                'video': {'id': '3qisu9NF1_0',
                          'title': 'Greater Than Less Than Song for Kids | Comparing Numbers to 1000',
                          'channel': 'Numberock', 'minutes': 4},
                'worksheet': {'instructions': 'Write <, > or =. Then order the numbers.',
                              'exercises': [
                                  '345 ___ 354',
                                  '809 ___ 798',
                                  '600 ___ 600',
                                  '152 ___ 125',
                                  'Order, smallest first: 482, 248, 824',
                                  'Order, biggest first: 905, 590, 950, 509',
                              ]},
                'quiz': [
                    ('mcq', 'Which number is the biggest?', ['589', '598', '859'], 2),
                    ('tf', '407 > 470', False),
                    ('mcq', 'Which is in order from smallest to biggest?',
                     ['216, 261, 612', '612, 261, 216', '261, 216, 612'], 0),
                    ('mcq', 'Which sign makes this true? 734 ___ 743', ['>', '<', '='], 1),
                ],
                'homework': {'title': 'Biggest number game',
                             'instructions': 'Play with a grown-up using cards or paper with the digits 0 to 9.',
                             'tasks': ['Pick 3 digits. Make the biggest number and the smallest number you can.',
                                       'Do it 3 times. Write the numbers down.',
                                       'Put all 6 numbers in order from smallest to biggest.'],
                             'marks': 12},
            },
        ],
    },

    # ------------------------------------------------------------------ ENGLISH HOME LANGUAGE
    (1, 'ENG-HL'): {
        'topic': 'Listening and speaking, first letter sounds and rhymes',
        'caps': 'Listening and Speaking: greet, introduce self, listen to and follow instructions; '
                'Phonics: phonemic awareness and first letter-sounds (s, a, t, i, p, n); '
                'rhymes and songs (Gr 1 Term 1 ATP)',
        'summary': 'Learners greet each other and say their names, learn the first letter sounds '
                   's, a, t, i, p and n, and listen for words that rhyme.',
        'days': [
            {
                'title': 'Hello! My name is ...',
                'minutes': 30,
                'objectives': [
                    'I can greet my teacher and my friends.',
                    'I can say my name in a full sentence.',
                    'I can listen when someone else speaks.',
                ],
                'notes': (
                    '<p>Welcome to Grade 1!</p>'
                    '<p>We say <strong>Good morning</strong> when we come to school.</p>'
                    '<p>We say our names like this: <em>"My name is Lerato."</em></p>'
                    '<ul><li>Look at the person.</li><li>Speak clearly.</li>'
                    '<li>Wait for your turn.</li><li>Listen with your ears and eyes.</li></ul>'
                ),
                'key_terms': [('greet', 'say hello'), ('listen', 'use your ears and pay attention')],
                'example': {'title': 'Class activity: the name circle', 'html': (
                    '<p>Sit in a circle. Pass a soft ball.</p>'
                    '<ol><li>When you have the ball, say: "Hello, my name is ...".</li>'
                    '<li>Everyone says: "Hello, ...!"</li><li>Pass the ball to the next friend.</li></ol>')},
                'video': {'id': 'yqlbn_nI2w8',
                          'title': "What's Your Name? featuring The Super Simple Puppets | Greeting Song | Super Simple Songs",
                          'channel': 'Super Simple Songs - Kids Songs', 'minutes': 3},
                'worksheet': {'instructions': 'Draw and write. Ask your teacher for help.',
                              'exercises': [
                                  'Draw your face in the box.',
                                  'Write your name: My name is __________.',
                                  'Draw your teacher.',
                                  'Draw a friend you met today.',
                                  'Colour the word: Hello',
                              ]},
                'quiz': [
                    ('mcq', 'What do we say when we meet someone?', ['Goodbye', 'Hello', 'Sorry'], 1),
                    ('tf', 'We talk when someone else is talking.', False),
                    ('mcq', 'How do we tell someone our name?',
                     ['My name is Sipho.', 'Sipho is name.', 'Name Sipho my.'], 0),
                ],
                'homework': {'title': 'Tell your family',
                             'instructions': 'Talk to your family about your first day.',
                             'tasks': ['Tell your family your teacher\'s name.',
                                       'Tell them the name of one new friend.',
                                       'Practise saying "Good morning, my name is ..."'],
                             'marks': 5},
            },
            {
                'title': 'Letter sounds s, a, t, i, p, n',
                'minutes': 30,
                'objectives': [
                    'I can say the sounds s, a, t, i, p and n.',
                    'I can hear the first sound in a word.',
                    'I can blend sounds to make a short word.',
                ],
                'notes': (
                    '<p>Letters make <strong>sounds</strong>.</p>'
                    '<ul><li><strong>s</strong> like a snake: sss (sun)</li>'
                    '<li><strong>a</strong> as in ant</li><li><strong>t</strong> as in tap</li>'
                    '<li><strong>i</strong> as in ink</li><li><strong>p</strong> as in pan</li>'
                    '<li><strong>n</strong> as in net</li></ul>'
                    '<p>Put sounds together: s-a-t makes <strong>sat</strong>.</p>'
                ),
                'key_terms': [('sound', 'what a letter says'),
                              ('blend', 'push sounds together to say a word')],
                'example': {'title': 'Class activity: sound and blend', 'html': (
                    '<p>Hold up the card <strong>p</strong>. Say "p, p, p".</p>'
                    '<p>Now blend with the teacher:</p>'
                    '<ul><li>p - i - n = pin</li><li>t - a - p = tap</li><li>s - i - t = sit</li></ul>'
                    '<p>Clap once for each sound.</p>')},
                'video': {'id': '4icYb-aTw9A',
                          'title': 'Jolly Phonics Songs Group 1 - Learn Letter Sounds s, a, t, i, p, n for Kids in American English',
                          'channel': 'Jolly Learning - The Home of Jolly Phonics', 'minutes': 5},
                'worksheet': {'instructions': 'Say the word. Write the first sound.',
                              'exercises': [
                                  '___un (sun)',
                                  '___nt (ant)',
                                  '___ap (tap)',
                                  '___an (pan)',
                                  '___et (net)',
                                  'Blend and read: s - a - t = ______',
                              ]},
                'quiz': [
                    ('mcq', 'What is the first sound in "sun"?', ['t', 'p', 's'], 2),
                    ('mcq', 'What word do t - i - n make?', ['tin', 'pin', 'tan'], 0),
                    ('tf', 'The word "pan" starts with the sound p.', True),
                    ('mcq', 'Which word starts with a?', ['net', 'ant', 'sit'], 1),
                ],
                'homework': {'title': 'Sound hunt',
                             'instructions': 'Look for things at home with a grown-up.',
                             'tasks': ['Find 2 things that start with s.',
                                       'Find 1 thing that starts with p.',
                                       'Write the letters s, a, t, i, p, n.'],
                             'marks': 6},
            },
            {
                'title': 'Words that rhyme',
                'minutes': 30,
                'objectives': [
                    'I can hear words that rhyme.',
                    'I can say a rhyme with my class.',
                    'I can find a word that rhymes with another word.',
                ],
                'notes': (
                    '<p>Words <strong>rhyme</strong> when they sound the same at the end.</p>'
                    '<ul><li>cat - hat - mat</li><li>pin - tin - bin</li><li>sun - fun - run</li></ul>'
                    '<p>Say this rhyme: <em>Hickory, dickory, dock. The mouse ran up the clock.</em></p>'
                    '<p>Dock and clock rhyme!</p>'
                ),
                'key_terms': [('rhyme', 'words that end with the same sound')],
                'example': {'title': 'Class activity: thumbs up for rhymes', 'html': (
                    '<p>The teacher says two words.</p>'
                    '<ul><li>cat, hat - thumbs up! They rhyme.</li>'
                    '<li>cat, dog - thumbs down. They do not rhyme.</li>'
                    '<li>pan, man - thumbs up!</li></ul>')},
                'video': {'id': 'RVophT8naUM',
                          'title': 'I Love to Rhyme | English Song for Kids | Rhyming for Children | Jack Hartmann',
                          'channel': 'Jack Hartmann Kids Music Channel', 'minutes': 3},
                'worksheet': {'instructions': 'Draw a line or write a word that rhymes.',
                              'exercises': [
                                  'cat rhymes with: hat / dog',
                                  'sun rhymes with: bed / fun',
                                  'pin rhymes with: tin / cup',
                                  'Write a word that rhymes with "pan": ______',
                                  'Write a word that rhymes with "bed": ______',
                              ]},
                'quiz': [
                    ('mcq', 'Which word rhymes with "cat"?', ['cup', 'dog', 'hat'], 2),
                    ('mcq', 'Which word rhymes with "sun"?', ['run', 'sit', 'tap'], 0),
                    ('tf', '"Dog" and "log" rhyme.', True),
                    ('tf', '"Pin" and "pan" rhyme.', False),
                ],
                'homework': {'title': 'Rhymes at home',
                             'instructions': 'Say rhymes with a grown-up.',
                             'tasks': ['Say a nursery rhyme you know to your family.',
                                       'Your grown-up says a word. You say a word that rhymes.',
                                       'Draw two things that rhyme (like cat and hat).'],
                             'marks': 6},
            },
        ],
    },

    (2, 'ENG-HL'): {
        'topic': 'Phonics revision, reading sight words and writing sentences',
        'caps': 'Phonics: revise single sounds and short vowels a, e, i, o, u; Reading: shared and '
                'group reading, high-frequency (sight) words; Handwriting and Writing: letter '
                'formation, sentences with capital letters and full stops (Gr 2 Term 1 ATP)',
        'summary': 'Learners revise short vowel sounds, read common sight words in short sentences, '
                   'and write neat sentences that start with a capital letter and end with a full stop.',
        'days': [
            {
                'title': 'Short vowel sounds a, e, i, o, u',
                'minutes': 30,
                'objectives': [
                    'I can say the five short vowel sounds.',
                    'I can hear the middle sound in a word.',
                    'I can read three-letter words.',
                ],
                'notes': (
                    '<p>The <strong>vowels</strong> are a, e, i, o and u.</p>'
                    '<ul><li>a as in <em>cat</em></li><li>e as in <em>bed</em></li>'
                    '<li>i as in <em>pig</em></li><li>o as in <em>dog</em></li>'
                    '<li>u as in <em>sun</em></li></ul>'
                    '<p>Most words have a vowel in them. Change the vowel and you get a new word: '
                    'pin, pan, pen.</p>'
                ),
                'key_terms': [('vowel', 'one of the letters a, e, i, o, u'),
                              ('consonant', 'all the other letters, like b, c, d')],
                'example': {'title': 'Class activity: change the middle sound', 'html': (
                    '<p>Start with <strong>b_g</strong>.</p>'
                    '<ul><li>Put in a: bag</li><li>Put in e: beg</li><li>Put in i: big</li>'
                    '<li>Put in u: bug</li></ul>'
                    '<p>Read each word and act it out.</p>')},
                'video': {'id': '-EbzKgs6Aiw', 'title': 'These Are the Short Vowel Sounds | Jack Hartmann',
                          'channel': 'Jack Hartmann Kids Music Channel', 'minutes': 4},
                'worksheet': {'instructions': 'Fill in the missing vowel. Read the word.',
                              'exercises': [
                                  'c ___ t (a pet that says meow)',
                                  'b ___ d (you sleep on it)',
                                  'p ___ g (a farm animal)',
                                  'd ___ g (a pet that barks)',
                                  's ___ n (it shines in the sky)',
                                  'Write two words with the vowel e: ______ ______',
                              ]},
                'quiz': [
                    ('mcq', 'What is the middle sound in "dog"?', ['a', 'o', 'u'], 1),
                    ('mcq', 'Which letter is a vowel?', ['e', 't', 'm'], 0),
                    ('tf', 'The words "pin", "pan" and "pen" have different vowels.', True),
                    ('mcq', 'Which word has the short u sound?', ['bed', 'cat', 'cup'], 2),
                ],
                'homework': {'title': 'Vowel words',
                             'instructions': 'Find and write words with a grown-up.',
                             'tasks': ['Write one three-letter word for each vowel: a, e, i, o, u.',
                                       'Read your words to a grown-up.'],
                             'marks': 10},
            },
            {
                'title': 'Reading sight words in sentences',
                'minutes': 30,
                'objectives': [
                    'I can read common sight words quickly.',
                    'I can read a short sentence with sight words.',
                    'I can answer a question about what I read.',
                ],
                'notes': (
                    '<p><strong>Sight words</strong> are words we see a lot. We learn to read them '
                    'quickly, without sounding out.</p>'
                    '<p>Some sight words: <em>the, is, was, said, I, you, my, we, go, to, they, have</em>.</p>'
                    '<p>Read: <em>I go to school. My school is big. We have fun.</em></p>'
                    '<ul><li>Point to each word as you read.</li><li>Read again to read faster.</li></ul>'
                ),
                'key_terms': [('sight word', 'a common word we know just by looking at it')],
                'example': {'title': 'Shared reading: Our first day', 'html': (
                    '<p><em>It was the first day of school. Tom said, "Hello!" '
                    'I said, "Hello, Tom!" We sat on the mat. They read a big book.</em></p>'
                    '<ol><li>Read the story with the teacher.</li>'
                    '<li>Find the words <strong>said</strong>, <strong>was</strong> and <strong>the</strong>.</li>'
                    '<li>Where did the children sit? (On the mat.)</li></ol>')},
                'video': {'id': 'gIZjrcG9pW0',
                          'title': 'New Sight Words 1 | Sight Words Kindergarten | High Frequency Words | Jump Out Words | Jack Hartmann',
                          'channel': 'Jack Hartmann Kids Music Channel', 'minutes': 6},
                'worksheet': {'instructions': 'Read the sentences. Fill in the missing sight word.',
                              'exercises': [
                                  'I ___ to school. (go / dog)',
                                  '___ name is Ben. (My / Me)',
                                  'The sun ___ hot. (is / in)',
                                  'Mom ___, "Come here." (sad / said)',
                                  'We ___ a cat. (have / hat)',
                                  'Write a sentence with the word "the".',
                              ]},
                'quiz': [
                    ('mcq', 'Which is a sight word?', ['the', 'zebra', 'trumpet'], 0),
                    ('mcq', 'Fill in: "I ___ happy."', ['at', 'am', 'on'], 1),
                    ('tf', 'We point to each word when we read.', True),
                    ('mcq', 'Read: "We sat on the mat." Where did we sit?', ['on a bus', 'in a tree', 'on the mat'], 2),
                ],
                'homework': {'title': 'Sight word practice',
                             'instructions': 'Read with a grown-up for 10 minutes.',
                             'tasks': ['Read the words: the, is, was, said, my, you, we, they.',
                                       'Read a short story or page with a grown-up. Find 3 sight words.',
                                       'Write 2 sentences using sight words.'],
                             'marks': 10},
            },
            {
                'title': 'Neat sentences: capital letters and full stops',
                'minutes': 30,
                'objectives': [
                    'I can form my letters neatly on the line.',
                    'I can start a sentence with a capital letter.',
                    'I can end a sentence with a full stop.',
                ],
                'notes': (
                    '<p>A <strong>sentence</strong> tells us one idea.</p>'
                    '<ul><li>It starts with a <strong>capital letter</strong>: The, My, We.</li>'
                    '<li>It ends with a <strong>full stop</strong> ( . )</li>'
                    '<li>We leave a finger space between words.</li></ul>'
                    '<p>Write neatly: sit up straight, hold your pencil well, and keep letters on the line.</p>'
                    '<p>Example: <em>My dog is brown.</em></p>'
                ),
                'key_terms': [('capital letter', 'a big letter, like A, B, C'),
                              ('full stop', 'the dot at the end of a sentence')],
                'example': {'title': 'Guided writing: fix the sentence', 'html': (
                    '<p>Look: <em>my cat is black</em></p>'
                    '<ol><li>Is there a capital letter at the start? No. Change m to <strong>M</strong>.</li>'
                    '<li>Is there a full stop at the end? No. Add <strong>.</strong></li></ol>'
                    '<p>Now: <strong>My cat is black.</strong></p>')},
                'video': {'id': 'gghvLTSS-eQ',
                          'title': "The Sentence Song - 'Capital Letter' + 'Full Stop' Version | Scratch Garden",
                          'channel': 'Scratch Garden', 'minutes': 3},
                'worksheet': {'instructions': 'Write each sentence correctly. Use a capital letter and a full stop.',
                              'exercises': [
                                  'the sun is hot',
                                  'i like to run',
                                  'we go to school',
                                  'my mom can sing',
                                  'Write your own sentence about your holiday.',
                              ]},
                'quiz': [
                    ('mcq', 'Which sentence is correct?',
                     ['the dog runs.', 'The dog runs.', 'The dog runs'], 1),
                    ('tf', 'A sentence ends with a full stop.', True),
                    ('mcq', 'What goes between words?', ['a finger space', 'a full stop', 'a capital letter'], 0),
                    ('tf', 'The word "I" is always written with a small letter.', False),
                ],
                'homework': {'title': 'Sentences about me',
                             'instructions': 'Write neatly. A grown-up can check your capital letters and full stops.',
                             'tasks': ['Write 3 sentences about yourself.',
                                       'Draw a picture to go with your sentences.'],
                             'marks': 10},
            },
        ],
    },

    (3, 'ENG-HL'): {
        'topic': 'Holiday news, consonant digraphs and writing sentences',
        'caps': 'Listening and Speaking: tell news in sequence; Phonics: consonant digraphs '
                '(sh, ch, th, wh); Writing: sentences with capital letters, full stops and '
                'question marks (Gr 3 Term 1 ATP)',
        'summary': 'Learners tell holiday news in order using sequence words, read and spell '
                   'words with sh, ch, th and wh, and write a short recount in correct sentences.',
        'days': [
            {
                'title': 'Telling my holiday news in order',
                'minutes': 35,
                'objectives': [
                    'I can tell my news in the right order.',
                    'I can use the words first, next, then and finally.',
                    'I can listen and ask a question about a friend\'s news.',
                ],
                'notes': (
                    '<p>When we tell <strong>news</strong>, we say what happened.</p>'
                    '<p>We tell it in <strong>order</strong> using <em>sequence words</em>:</p>'
                    '<ul><li><strong>First</strong>, we went to Gran\'s house.</li>'
                    '<li><strong>Next</strong>, we baked a cake.</li>'
                    '<li><strong>Then</strong>, we ate it with tea.</li>'
                    '<li><strong>Finally</strong>, we went home.</li></ul>'
                    '<p>Good listeners look at the speaker and ask a question at the end: '
                    '<em>"What kind of cake was it?"</em></p>'
                ),
                'key_terms': [('news', 'something that happened to you'),
                              ('sequence words', 'words that show order: first, next, then, finally')],
                'example': {'title': 'Class activity: news partners', 'html': (
                    '<ol><li>Think of one thing you did in the holidays.</li>'
                    '<li>Hold up four fingers. Say one part of your news for each finger: first, next, then, finally.</li>'
                    '<li>Your partner listens and asks one question.</li>'
                    '<li>Swap.</li></ol>')},
                'video': {'id': 'uv3ZHHRlvQQ', 'title': 'FIRST, NEXT, THEN, FINALLY SONG / Sequence event song',
                          'channel': "SIR BON'S MUSIC ROOM", 'minutes': 3},
                'worksheet': {'instructions': 'Use first, next, then and finally.',
                              'exercises': [
                                  'Put in order: Then I ate breakfast. / First I woke up. / Finally I went to school. / Next I got dressed.',
                                  'Finish: First, I ______________.',
                                  'Finish: Next, I ______________.',
                                  'Finish: Then, I ______________.',
                                  'Finish: Finally, I ______________.',
                                  'Write one question you could ask a friend about their holiday.',
                              ]},
                'quiz': [
                    ('mcq', 'Which word do we use to start our news?', ['Finally', 'First', 'Then'], 1),
                    ('mcq', 'Which word tells us it is the end?', ['Next', 'First', 'Finally'], 2),
                    ('tf', 'A good listener looks at the speaker.', True),
                    ('mcq', 'Which is a good question about news?',
                     ['Where did you go?', 'Go you where?', 'You went.'], 0),
                ],
                'homework': {'title': 'Family news',
                             'instructions': 'Talk with a grown-up about something you did together.',
                             'tasks': ['Tell your grown-up your holiday news using first, next, then, finally.',
                                       'Ask your grown-up to tell you their news. Ask them one question.'],
                             'marks': 10},
            },
            {
                'title': 'Consonant digraphs: sh, ch, th, wh',
                'minutes': 35,
                'objectives': [
                    'I can say the sounds sh, ch, th and wh.',
                    'I can read and spell words with these sounds.',
                    'I can sort words by their digraph.',
                ],
                'notes': (
                    '<p>A <strong>digraph</strong> is two letters that make <em>one</em> sound.</p>'
                    '<ul><li><strong>sh</strong> as in ship, fish</li>'
                    '<li><strong>ch</strong> as in chip, lunch</li>'
                    '<li><strong>th</strong> as in thin, bath</li>'
                    '<li><strong>wh</strong> as in when, whale</li></ul>'
                    '<p>Digraphs can be at the start or the end of a word.</p>'
                    '<p>Many question words start with wh: <em>what, when, where, which, why</em>.</p>'
                ),
                'key_terms': [('digraph', 'two letters that make one sound')],
                'example': {'title': 'Class activity: sort the words', 'html': (
                    '<p>Read the words: <em>shop, chin, thumb, whip, dish, much, with, chop</em>.</p>'
                    '<ul><li>sh: shop, dish</li><li>ch: chin, much, chop</li>'
                    '<li>th: thumb, with</li><li>wh: whip</li></ul>')},
                'video': {'id': 'NK8_Tvu6bJk',
                          'title': 'Digraphs | Phonics Song for Children | Phonemic Awareness | Jack Hartmann',
                          'channel': 'Jack Hartmann Kids Music Channel', 'minutes': 4},
                'worksheet': {'instructions': 'Fill in sh, ch, th or wh.',
                              'exercises': [
                                  '___ip (a boat on the sea)',
                                  'fi___ (it swims)',
                                  '___eese (made from milk)',
                                  'ba___ (you wash in it)',
                                  '___ale (a very big sea animal)',
                                  'lun___ (a meal in the middle of the day)',
                                  'Write two question words that start with wh.',
                              ]},
                'quiz': [
                    ('mcq', 'Which word has the digraph "sh"?', ['chip', 'fish', 'thin'], 1),
                    ('mcq', 'Which word starts with "th"?', ['thumb', 'whip', 'shop'], 0),
                    ('tf', 'A digraph is two letters that make one sound.', True),
                    ('mcq', 'Which word ends with "ch"?', ['wish', 'with', 'much'], 2),
                ],
                'homework': {'title': 'Digraph hunt',
                             'instructions': 'Look in a book, newspaper or on packets at home.',
                             'tasks': ['Find and write 2 words with sh and 2 words with ch.',
                                       'Find and write 1 word with th and 1 word with wh.',
                                       'Read your words to a grown-up.'],
                             'marks': 12},
            },
            {
                'title': 'Writing my holiday recount',
                'minutes': 35,
                'objectives': [
                    'I can write 4 or 5 sentences in the right order.',
                    'I can use capital letters, full stops and question marks.',
                    'I can check my writing and fix mistakes.',
                ],
                'notes': (
                    '<p>A <strong>recount</strong> tells what happened, in order.</p>'
                    '<ul><li>Start every sentence with a <strong>capital letter</strong>.</li>'
                    '<li>Names of people and places also start with capitals: Thandi, Durban.</li>'
                    '<li>End a telling sentence with a <strong>full stop</strong> (.)</li>'
                    '<li>End an asking sentence with a <strong>question mark</strong> (?)</li></ul>'
                    '<p>Use sequence words from Day 1. Read your work again to check it.</p>'
                ),
                'key_terms': [('recount', 'writing that tells what happened in order'),
                              ('question mark', 'the mark (?) at the end of a question')],
                'example': {'title': 'Guided writing: check and fix', 'html': (
                    '<p>Read: <em>first we went to durban. we swam in the sea. did you go to the sea</em></p>'
                    '<ol><li>Capital letters: <strong>F</strong>irst, <strong>D</strong>urban, <strong>W</strong>e, <strong>D</strong>id.</li>'
                    '<li>Full stops after "Durban" and "sea".</li>'
                    '<li>A question mark after the question.</li></ol>'
                    '<p>Fixed: <strong>First we went to Durban. We swam in the sea. Did you go to the sea?</strong></p>')},
                'video': {'id': 'ZZTvXJvJNnA', 'title': 'Nessy Writing Strategy | Capital Letters and Full Stops',
                          'channel': 'Nessy', 'minutes': 3},
                'worksheet': {'instructions': 'Rewrite correctly, then write your own recount.',
                              'exercises': [
                                  'we went to the park',
                                  'my friend sipho lives in soweto',
                                  'where did you go',
                                  'Write 4 sentences about your holiday. Use first, next, then, finally.',
                                  'Check: Did every sentence start with a capital letter?',
                              ]},
                'quiz': [
                    ('mcq', 'Which mark ends a question?', ['.', '?', ','], 1),
                    ('mcq', 'Which is written correctly?',
                     ['We visited Cape Town.', 'we visited cape town.', 'We visited cape Town'], 0),
                    ('tf', 'Names of places start with a capital letter.', True),
                    ('mcq', 'A recount tells ...', ['how to make a cake', 'facts about lions', 'what happened, in order'], 2),
                ],
                'homework': {'title': 'Family recount',
                             'instructions': 'Write about something you did with your family. A grown-up can help you check it.',
                             'tasks': ['Write 4 or 5 sentences in order.',
                                       'Use at least one question in your writing.',
                                       'Draw a picture to go with it.'],
                             'marks': 15},
            },
        ],
    },

    # ------------------------------------------------------------------ ISIZULU FAL
    (1, 'ZUL-FAL'): {
        'topic': 'Ukubingelela: greetings, classroom instructions and my name',
        'caps': 'Listening and Speaking: greet and respond to greetings; listen to and respond to '
                'simple classroom instructions; introduce self (isiZulu FAL Gr 1 Term 1 ATP)',
        'summary': 'Learners greet in isiZulu (Sawubona / Sanibonani), follow simple classroom '
                   'instructions, and say their name and age.',
        'days': [
            {
                'title': 'Sawubona! Saying hello',
                'minutes': 25,
                'objectives': [
                    'I can say hello in isiZulu.',
                    'I can answer when someone greets me.',
                    'I can say thank you.',
                ],
                'notes': (
                    '<p>Let us greet in isiZulu!</p>'
                    '<ul><li><strong>Sawubona</strong> - Hello (to one person)</li>'
                    '<li><strong>Sanibonani</strong> - Hello (to many people)</li>'
                    '<li><strong>Yebo</strong> - Yes (we say "Yebo, sawubona" to answer)</li>'
                    '<li><strong>Ngiyabonga</strong> - Thank you</li></ul>'
                    '<p>Teacher: <em>Sanibonani, bafundi!</em> (Hello, learners!)<br>'
                    'Class: <em>Yebo, thisha!</em> (Yes, teacher!)</p>'
                ),
                'key_terms': [('Sawubona', 'Hello (to one person)'),
                              ('Sanibonani', 'Hello (to many people)'),
                              ('Ngiyabonga', 'Thank you')],
                'example': {'title': 'Class activity: greet a friend', 'html': (
                    '<p>Walk around the class. Shake hands with a friend.</p>'
                    '<p>A: <em>Sawubona!</em> (Hello!)<br>B: <em>Yebo, sawubona!</em> (Yes, hello!)</p>'
                    '<p>Now greet a group of three friends: <em>Sanibonani!</em></p>')},
                'video': {'id': 'kXyQg-rgJ4E', 'title': 'Zulu Greetings Song | Hello, Please, Thank You',
                          'channel': 'Mama Zulu', 'minutes': 3},
                'worksheet': {'instructions': 'Match the isiZulu word to the English. Draw a line.',
                              'exercises': [
                                  'Sawubona          Thank you',
                                  'Ngiyabonga        Hello (to one person)',
                                  'Yebo              Hello (to many people)',
                                  'Sanibonani        Yes',
                                  'Draw two friends saying Sawubona.',
                              ]},
                'quiz': [
                    ('mcq', 'How do we say hello to ONE person?', ['Ngiyabonga', 'Sawubona', 'Yebo'], 1),
                    ('mcq', '"Ngiyabonga" means ...', ['Thank you', 'Hello', 'Yes'], 0),
                    ('tf', '"Sanibonani" is how we greet many people.', True),
                ],
                'homework': {'title': 'Greet your family',
                             'instructions': 'Say hello in isiZulu at home.',
                             'tasks': ['Greet one person at home with "Sawubona!"',
                                       'Greet everyone at supper with "Sanibonani!"',
                                       'Say "Ngiyabonga" when someone helps you.'],
                             'marks': 5},
            },
            {
                'title': 'Sukumani! Hlalani phansi! Classroom instructions',
                'minutes': 25,
                'objectives': [
                    'I can listen to an instruction in isiZulu.',
                    'I can do the action the teacher says.',
                ],
                'notes': (
                    '<p>The teacher gives instructions to the class in isiZulu:</p>'
                    '<ul><li><strong>Sukumani</strong> - Stand up</li>'
                    '<li><strong>Hlalani phansi</strong> - Sit down</li>'
                    '<li><strong>Lalelani</strong> - Listen</li>'
                    '<li><strong>Thulani</strong> - Be quiet</li>'
                    '<li><strong>Bukani</strong> - Look</li></ul>'
                    '<p>Listen. Then do the action!</p>'
                ),
                'key_terms': [('Sukumani', 'Stand up (to many)'),
                              ('Hlalani phansi', 'Sit down (to many)'),
                              ('Lalelani', 'Listen (to many)')],
                'example': {'title': 'Class game: Thisha uthi ... (Teacher says ...)', 'html': (
                    '<p>Play like "Simon says".</p>'
                    '<ul><li>Teacher: <em>Thisha uthi: Sukumani!</em> Everyone stands up.</li>'
                    '<li>Teacher: <em>Thisha uthi: Hlalani phansi!</em> Everyone sits down.</li>'
                    '<li>Teacher: <em>Thulani!</em> (no "Thisha uthi") - do not move!</li></ul>')},
                'video': {'id': 'cKw2GCmTueM', 'title': 'isiZulu Action Song for Kids | Izenzo',
                          'channel': 'Mama Zulu', 'minutes': 3},
                'worksheet': {'instructions': 'Draw a picture for each instruction.',
                              'exercises': [
                                  'Sukumani (Stand up) - draw a child standing.',
                                  'Hlalani phansi (Sit down) - draw a child sitting.',
                                  'Lalelani (Listen) - draw a big ear.',
                                  'Bukani (Look) - draw two eyes.',
                              ]},
                'quiz': [
                    ('mcq', '"Sukumani" means ...', ['Sit down', 'Listen', 'Stand up'], 2),
                    ('mcq', 'The teacher says "Hlalani phansi". What do you do?',
                     ['Sit down', 'Stand up', 'Sing'], 0),
                    ('tf', '"Lalelani" means "Listen".', True),
                ],
                'homework': {'title': 'Teach your family',
                             'instructions': 'Play "Thisha uthi" at home.',
                             'tasks': ['Teach a grown-up what Sukuma (stand up) and Hlala phansi (sit down) mean.',
                                       'Give your family the instructions and see if they do the actions.'],
                             'marks': 5},
            },
            {
                'title': 'Igama lami ngu... My name is ...',
                'minutes': 25,
                'objectives': [
                    'I can say my name in isiZulu.',
                    'I can ask a friend their name.',
                    'I can say how old I am.',
                ],
                'notes': (
                    '<p>Ask: <strong>Ngubani igama lakho?</strong> - What is your name?</p>'
                    '<p>Answer: <strong>Igama lami ngu-Zola.</strong> - My name is Zola.</p>'
                    '<p>Ask: <strong>Uneminyaka emingaki?</strong> - How old are you?</p>'
                    '<p>Answer: <strong>Ngineminyaka eyisithupha.</strong> - I am six years old.<br>'
                    '<em>Ngineminyaka eyisikhombisa.</em> - I am seven years old.</p>'
                ),
                'key_terms': [('igama', 'name'), ('lami', 'my'), ('lakho', 'your')],
                'example': {'title': 'Dialogue: meeting a new friend', 'html': (
                    '<p>Lwazi: <em>Sawubona!</em> (Hello!)<br>'
                    'Amy: <em>Yebo, sawubona!</em> (Yes, hello!)<br>'
                    'Lwazi: <em>Ngubani igama lakho?</em> (What is your name?)<br>'
                    'Amy: <em>Igama lami ngu-Amy.</em> (My name is Amy.)<br>'
                    'Lwazi: <em>Uneminyaka emingaki?</em> (How old are you?)<br>'
                    'Amy: <em>Ngineminyaka eyisithupha.</em> (I am six years old.)</p>'
                    '<p>Practise with a partner. Use your own name.</p>')},
                'video': {'id': '7ElrJ8c7dZM',
                          'title': 'How to say "my name is..." and ask "what is your name?" in Zulu - One Minute Zulu Lesson 6',
                          'channel': 'Coffee Break Languages', 'minutes': 2},
                'worksheet': {'instructions': 'Draw and write. Your teacher will help you.',
                              'exercises': [
                                  'Draw yourself.',
                                  'Igama lami ngu- __________. (My name is ...)',
                                  'Ngineminyaka ____. (I am ... years old) Draw candles for your age.',
                                  'Draw a friend. Write their name.',
                              ]},
                'quiz': [
                    ('mcq', 'How do you ask "What is your name?"',
                     ['Ngiyabonga', 'Ngubani igama lakho?', 'Sanibonani'], 1),
                    ('mcq', '"Igama lami ngu-Sipho" means ...',
                     ['My name is Sipho.', 'Sipho is six.', 'Hello, Sipho.'], 0),
                    ('tf', '"Ngineminyaka eyisithupha" means "I am six years old".', True),
                ],
                'homework': {'title': 'My name in isiZulu',
                             'instructions': 'Practise with a grown-up.',
                             'tasks': ['Say "Igama lami ngu-..." with your own name.',
                                       'Ask a grown-up "Ngubani igama lakho?" and listen to the answer.'],
                             'marks': 5},
            },
        ],
    },

    (2, 'ZUL-FAL'): {
        'topic': 'Greetings, imibala (colours) and izinombolo (numbers 1-10)',
        'caps': 'Listening and Speaking: greetings and asking how someone is; vocabulary themes '
                'colours and numbers; respond to simple questions (isiZulu FAL Gr 2 Term 1 ATP)',
        'summary': 'Learners greet and ask how someone is (Unjani? Ngiyaphila), and name colours '
                   'and count from one to ten in isiZulu.',
        'days': [
            {
                'title': 'Unjani? Ngiyaphila! How are you?',
                'minutes': 25,
                'objectives': [
                    'I can greet and ask "How are you?" in isiZulu.',
                    'I can answer "I am well".',
                    'I can say goodbye.',
                ],
                'notes': (
                    '<ul><li><strong>Sawubona</strong> - Hello (to one)</li>'
                    '<li><strong>Unjani?</strong> - How are you? (to one)</li>'
                    '<li><strong>Ngiyaphila</strong> - I am well</li>'
                    '<li><strong>Wena unjani?</strong> - And how are you?</li>'
                    '<li><strong>Nami ngiyaphila</strong> - I am also well</li>'
                    '<li><strong>Hamba kahle</strong> - Go well (to someone leaving)</li>'
                    '<li><strong>Sala kahle</strong> - Stay well (when you leave)</li></ul>'
                ),
                'key_terms': [('Unjani?', 'How are you?'), ('Ngiyaphila', 'I am well'),
                              ('Hamba kahle', 'Go well / goodbye')],
                'example': {'title': 'Dialogue: at the school gate', 'html': (
                    '<p>Nomsa: <em>Sawubona, Peter!</em> (Hello, Peter!)<br>'
                    'Peter: <em>Yebo, sawubona, Nomsa! Unjani?</em> (Yes, hello, Nomsa! How are you?)<br>'
                    'Nomsa: <em>Ngiyaphila. Wena unjani?</em> (I am well. And you?)<br>'
                    'Peter: <em>Nami ngiyaphila, ngiyabonga.</em> (I am also well, thank you.)</p>'
                    '<p>Act it out with a partner.</p>')},
                'video': {'id': 'A6o5Mrrd4Ww',
                          'title': 'Learn isiZulu Greetings | How to Greet & Respond in Zulu for Beginners',
                          'channel': 'Zulu Lessons with Thando', 'minutes': 5},
                'worksheet': {'instructions': 'Fill in the missing word. Use: Unjani, Ngiyaphila, Sawubona, kahle.',
                              'exercises': [
                                  'A: ________, Thabo! (Hello)',
                                  'B: Yebo, sawubona! ________? (How are you?)',
                                  'A: ________. (I am well)',
                                  'B: Hamba ________! (Go well)',
                                  'Draw two friends greeting each other.',
                              ]},
                'quiz': [
                    ('mcq', '"Unjani?" means ...', ['Thank you', 'How are you?', 'Go well'], 1),
                    ('mcq', 'How do you say "I am well"?', ['Ngiyaphila', 'Sala kahle', 'Yebo'], 0),
                    ('tf', 'We say "Hamba kahle" to someone who is leaving.', True),
                    ('mcq', '"Nami ngiyaphila" means ...', ['I am six', 'Hello to all', 'I am also well'], 2),
                ],
                'homework': {'title': 'Greet at home',
                             'instructions': 'Use your isiZulu greetings with your family.',
                             'tasks': ['Ask a grown-up "Unjani?" and teach them to say "Ngiyaphila".',
                                       'Say "Hamba kahle" or "Sala kahle" when someone leaves.'],
                             'marks': 5},
            },
            {
                'title': 'Imibala: colours',
                'minutes': 25,
                'objectives': [
                    'I can name 6 colours in isiZulu.',
                    'I can point to a colour when I hear it.',
                ],
                'notes': (
                    '<p><strong>Imibala</strong> means colours.</p>'
                    '<ul><li><strong>bomvu</strong> - red</li><li><strong>phuzi</strong> - yellow</li>'
                    '<li><strong>luhlaza okwesibhakabhaka</strong> - blue</li>'
                    '<li><strong>luhlaza okotshani</strong> - green</li>'
                    '<li><strong>mnyama</strong> - black</li><li><strong>mhlophe</strong> - white</li></ul>'
                    '<p><em>Ilanga liphuzi.</em> - The sun is yellow.<br>'
                    '<em>Inja imnyama.</em> - The dog is black.</p>'
                ),
                'key_terms': [('imibala', 'colours'), ('bomvu', 'red'), ('phuzi', 'yellow')],
                'example': {'title': 'Class game: Thinta umbala! (Touch the colour!)', 'html': (
                    '<p>The teacher says a colour in isiZulu.</p>'
                    '<ul><li><em>Bomvu!</em> - touch something red.</li>'
                    '<li><em>Mhlophe!</em> - touch something white.</li>'
                    '<li><em>Luhlaza okotshani!</em> - touch something green.</li></ul>')},
                'video': {'id': '58MtogV2A5I', 'title': 'Imibala-Learn Colours in isiZulu',
                          'channel': 'Mama Zulu', 'minutes': 3},
                'worksheet': {'instructions': 'Colour each box in the right colour.',
                              'exercises': [
                                  'bomvu  [     ]',
                                  'phuzi  [     ]',
                                  'luhlaza okwesibhakabhaka  [     ]',
                                  'luhlaza okotshani  [     ]',
                                  'mnyama  [     ]',
                                  'Draw the sun and colour it: Ilanga liphuzi.',
                              ]},
                'quiz': [
                    ('mcq', '"Bomvu" means ...', ['blue', 'black', 'red'], 2),
                    ('mcq', 'Which word means white?', ['mhlophe', 'mnyama', 'phuzi'], 0),
                    ('tf', '"Ilanga liphuzi" means "The sun is yellow".', True),
                    ('mcq', 'Grass is green. Green is ...', ['bomvu', 'luhlaza okotshani', 'mnyama'], 1),
                ],
                'homework': {'title': 'Colour hunt',
                             'instructions': 'Find colours at home with a grown-up.',
                             'tasks': ['Find something bomvu (red) and something phuzi (yellow).',
                                       'Tell a grown-up the isiZulu colour of your shirt.',
                                       'Draw 3 things and write the isiZulu colour under each.'],
                             'marks': 6},
            },
            {
                'title': 'Izinombolo: counting 1 to 10',
                'minutes': 25,
                'objectives': [
                    'I can count from 1 to 10 in isiZulu.',
                    'I can say how many things I see.',
                ],
                'notes': (
                    '<p>Let us count in isiZulu!</p>'
                    '<ol><li>kunye</li><li>kubili</li><li>kuthathu</li><li>kune</li><li>kuhlanu</li>'
                    '<li>isithupha</li><li>isikhombisa</li><li>isishiyagalombili</li>'
                    '<li>isishiyagalolunye</li><li>ishumi</li></ol>'
                    '<p>Hint: <em>isithupha</em> means thumb. We count to 5 on one hand, '
                    'then 6 is the thumb of the other hand!</p>'
                ),
                'key_terms': [('izinombolo', 'numbers'), ('kunye', 'one'), ('ishumi', 'ten')],
                'example': {'title': 'Class activity: count and clap', 'html': (
                    '<p>Count and clap with the teacher: <em>kunye</em> (clap), <em>kubili</em> (clap), '
                    '<em>kuthathu</em> (clap) ... up to <em>ishumi</em>.</p>'
                    '<p>Now count 4 books: kunye, kubili, kuthathu, kune. There are 4 (kune).</p>')},
                'video': {'id': '6G12fe80JMU', 'title': '🔢🎵 Ake Sibale! | Count from 1 to 10 in isiZulu',
                          'channel': 'Mama Zulu', 'minutes': 3},
                'worksheet': {'instructions': 'Write the number next to the isiZulu word.',
                              'exercises': [
                                  'kubili = ___',
                                  'kuhlanu = ___',
                                  'isithupha = ___',
                                  'ishumi = ___',
                                  'kuthathu = ___',
                                  'Draw kune (4) balls.',
                              ]},
                'quiz': [
                    ('mcq', 'What is 3 in isiZulu?', ['kubili', 'kune', 'kuthathu'], 2),
                    ('mcq', '"Kuhlanu" is ...', ['5', '4', '6'], 0),
                    ('tf', '"Ishumi" means ten.', True),
                    ('mcq', 'Which word means one?', ['ishumi', 'kunye', 'kubili'], 1),
                ],
                'homework': {'title': 'Count in isiZulu',
                             'instructions': 'Count things at home in isiZulu.',
                             'tasks': ['Count the cups in the kitchen in isiZulu.',
                                       'Teach a grown-up to count to five: kunye, kubili, kuthathu, kune, kuhlanu.'],
                             'marks': 5},
            },
        ],
    },

    (3, 'ZUL-FAL'): {
        'topic': 'Greetings, umzimba wami (my body) and talking about myself',
        'caps': 'Listening and Speaking: greetings with respect; respond to instructions using '
                'vocabulary of the body; short dialogues to introduce self (isiZulu FAL Gr 3 Term 1 ATP)',
        'summary': 'Learners greet adults and friends politely, name parts of the body and follow '
                   '"Thinta ..." (touch ...) instructions, then introduce themselves in a short dialogue.',
        'days': [
            {
                'title': 'Greeting adults and friends politely',
                'minutes': 30,
                'objectives': [
                    'I can greet an adult with respect.',
                    'I can greet one person and a group.',
                    'I can use please and thank you in isiZulu.',
                ],
                'notes': (
                    '<p>In isiZulu we show respect when we greet adults.</p>'
                    '<ul><li><strong>Sawubona, mama.</strong> - Hello, mother / madam.</li>'
                    '<li><strong>Sawubona, baba.</strong> - Hello, father / sir.</li>'
                    '<li><strong>Sawubona, thisha.</strong> - Hello, teacher.</li>'
                    '<li><strong>Sanibonani, bangane.</strong> - Hello, friends.</li>'
                    '<li><strong>Ngiyacela</strong> - Please</li>'
                    '<li><strong>Ngiyabonga</strong> - Thank you</li></ul>'
                    '<p><em>Ngicela ipensela.</em> - May I have a pencil, please?</p>'
                ),
                'key_terms': [('mama', 'mother / madam'), ('baba', 'father / sir'),
                              ('Ngiyacela', 'Please')],
                'example': {'title': 'Dialogue: in the classroom', 'html': (
                    '<p>Learner: <em>Sawubona, thisha.</em> (Hello, teacher.)<br>'
                    'Teacher: <em>Yebo, sawubona. Unjani?</em> (Yes, hello. How are you?)<br>'
                    'Learner: <em>Ngiyaphila, ngiyabonga. Ninjani?</em> (I am well, thank you. How are you?)<br>'
                    'Teacher: <em>Ngiyaphila.</em> (I am well.)</p>'
                    '<p>Note: children often use <em>Ninjani?</em> (plural) to an adult to show respect.</p>')},
                'video': {'id': 'H9QqUa3jwCQ',
                          'title': 'Learn isiZulu Greetings for Kids | Fun Zulu Language Lesson for Toddlers & Preschoolers',
                          'channel': 'Preschool Learning Videos with Ms Aimee', 'minutes': 4},
                'worksheet': {'instructions': 'How would you greet each person? Write the greeting.',
                              'exercises': [
                                  'Your teacher: ______________',
                                  'Your father or grandfather: ______________',
                                  'Your mother or grandmother: ______________',
                                  'A group of friends: ______________',
                                  'Ask for a pencil politely: ______________',
                                  'Say thank you: ______________',
                              ]},
                'quiz': [
                    ('mcq', 'How do you greet your teacher?', ['Sanibonani, bangane', 'Sawubona, thisha', 'Hamba kahle'], 1),
                    ('mcq', '"Ngiyacela" means ...', ['Please', 'Thank you', 'Hello'], 0),
                    ('tf', '"Sawubona, baba" is a greeting for a man.', True),
                    ('mcq', 'How do you greet a group of friends?', ['Sawubona, mama', 'Ngiyabonga', 'Sanibonani, bangane'], 2),
                ],
                'homework': {'title': 'Polite greetings',
                             'instructions': 'Greet the adults at home in isiZulu.',
                             'tasks': ['Greet an adult at home with "Sawubona, mama" or "Sawubona, baba".',
                                       'Use "Ngiyacela" and "Ngiyabonga" at supper time.',
                                       'Write the greetings in your book with the English meaning.'],
                             'marks': 10},
            },
            {
                'title': 'Umzimba wami: parts of my body',
                'minutes': 30,
                'objectives': [
                    'I can name 8 parts of the body in isiZulu.',
                    'I can follow "Thinta ..." (touch ...) instructions.',
                ],
                'notes': (
                    '<p><strong>Umzimba wami</strong> means my body.</p>'
                    '<ul><li><strong>ikhanda</strong> - head</li><li><strong>amehlo</strong> - eyes</li>'
                    '<li><strong>izindlebe</strong> - ears</li><li><strong>ikhala</strong> - nose</li>'
                    '<li><strong>umlomo</strong> - mouth</li><li><strong>izandla</strong> - hands</li>'
                    '<li><strong>imilenze</strong> - legs</li><li><strong>izinyawo</strong> - feet</li></ul>'
                    '<p><em>Thinta ikhanda lakho.</em> - Touch your head.<br>'
                    '<em>Nginamehlo amabili.</em> - I have two eyes.</p>'
                ),
                'key_terms': [('umzimba', 'body'), ('thinta', 'touch'), ('ikhanda', 'head')],
                'example': {'title': 'Class game: Thinta! (Touch!)', 'html': (
                    '<ul><li><em>Thinta ikhanda lakho.</em> (Touch your head.)</li>'
                    '<li><em>Thinta ikhala lakho.</em> (Touch your nose.)</li>'
                    '<li><em>Thinta umlomo wakho.</em> (Touch your mouth.)</li>'
                    '<li><em>Thinta izindlebe zakho.</em> (Touch your ears.)</li></ul>'
                    '<p>Go faster and faster!</p>')},
                'video': {'id': 'LoR65cHb8WE',
                          'title': 'Learn Body Parts in isiZulu & English 🎵 Umzimba Wami Song for Kids | ZuluTotsTV',
                          'channel': 'ZuluTotsTV', 'minutes': 3},
                'worksheet': {'instructions': 'Draw a child. Label the body parts in isiZulu.',
                              'exercises': [
                                  'head = __________',
                                  'eyes = __________',
                                  'nose = __________',
                                  'mouth = __________',
                                  'hands = __________',
                                  'feet = __________',
                                  'Complete: Nginamehlo ________. (I have two eyes.)',
                              ]},
                'quiz': [
                    ('mcq', '"Ikhala" means ...', ['ear', 'mouth', 'nose'], 2),
                    ('mcq', 'Which word means hands?', ['izandla', 'izinyawo', 'amehlo'], 0),
                    ('tf', '"Thinta ikhanda lakho" means "Touch your head".', True),
                    ('mcq', '"Umlomo" means ...', ['leg', 'mouth', 'eye'], 1),
                ],
                'homework': {'title': 'Teach the body game',
                             'instructions': 'Play "Thinta!" with someone at home.',
                             'tasks': ['Teach a grown-up 5 body words in isiZulu.',
                                       'Play "Thinta!" with them for 5 minutes.',
                                       'Write the 5 words with their English meanings.'],
                             'marks': 10},
            },
            {
                'title': 'Ukuzazisa: talking about myself',
                'minutes': 30,
                'objectives': [
                    'I can say my name and age in isiZulu.',
                    'I can ask a friend questions about themselves.',
                    'I can take part in a short dialogue.',
                ],
                'notes': (
                    '<p><strong>Ukuzazisa</strong> means to introduce yourself.</p>'
                    '<ul><li><strong>Ngubani igama lakho?</strong> - What is your name?</li>'
                    '<li><strong>Igama lami ngu-...</strong> - My name is ...</li>'
                    '<li><strong>Uneminyaka emingaki?</strong> - How old are you?</li>'
                    '<li><strong>Ngineminyaka eyisishiyagalombili.</strong> - I am eight years old.</li>'
                    '<li><strong>Ngineminyaka eyisishiyagalolunye.</strong> - I am nine years old.</li>'
                    '<li><strong>Ngiyajabula ukukwazi.</strong> - I am happy to meet you.</li></ul>'
                ),
                'key_terms': [('ukuzazisa', 'introducing yourself'),
                              ('iminyaka', 'years'), ('Ngiyajabula', 'I am happy')],
                'example': {'title': 'Dialogue: a new learner', 'html': (
                    '<p>Sizwe: <em>Sawubona! Ngubani igama lakho?</em> (Hello! What is your name?)<br>'
                    'Lily: <em>Yebo, sawubona. Igama lami ngu-Lily.</em> (Yes, hello. My name is Lily.)<br>'
                    'Sizwe: <em>Uneminyaka emingaki?</em> (How old are you?)<br>'
                    'Lily: <em>Ngineminyaka eyisishiyagalombili. Wena?</em> (I am eight. And you?)<br>'
                    'Sizwe: <em>Nami. Ngiyajabula ukukwazi!</em> (Me too. Happy to meet you!)</p>')},
                'video': {'id': '7ElrJ8c7dZM',
                          'title': 'How to say "my name is..." and ask "what is your name?" in Zulu - One Minute Zulu Lesson 6',
                          'channel': 'Coffee Break Languages', 'minutes': 2},
                'worksheet': {'instructions': 'Answer in isiZulu. Then write a short dialogue.',
                              'exercises': [
                                  'Ngubani igama lakho? ______________',
                                  'Uneminyaka emingaki? ______________',
                                  'How do you say "I am happy to meet you"? ______________',
                                  'Write a 4-line dialogue between you and a new friend.',
                              ]},
                'quiz': [
                    ('mcq', '"Uneminyaka emingaki?" means ...',
                     ['What is your name?', 'How are you?', 'How old are you?'], 2),
                    ('mcq', 'How do you say "I am eight years old"?',
                     ['Ngineminyaka eyisishiyagalombili.', 'Igama lami ngu-eight.', 'Ngiyaphila.'], 0),
                    ('tf', '"Ukuzazisa" means introducing yourself.', True),
                ],
                'homework': {'title': 'Introduce yourself',
                             'instructions': 'Practise your dialogue with a grown-up.',
                             'tasks': ['Say your name and age in isiZulu to a grown-up.',
                                       'Ask them "Ngubani igama lakho?" and "Uneminyaka emingaki?"',
                                       'Write your dialogue neatly in your book.'],
                             'marks': 10},
            },
        ],
    },

    # ------------------------------------------------------------------ LIFE SKILLS
    (1, 'LIFE-SK'): {
        'topic': 'Me and my school',
        'caps': 'Beginning Knowledge and Personal and Social Well-being: My school (my classroom, '
                'people at school, school rules and safety); Creative Arts; Physical Education: '
                'moving safely in space (Gr 1 Term 1 ATP)',
        'summary': 'Learners get to know their classroom and the people at school, learn simple '
                   'school rules, and practise moving safely in a movement game.',
        'days': [
            {
                'title': 'My classroom and the people at school',
                'minutes': 30,
                'objectives': [
                    'I can name things in my classroom.',
                    'I can name people who help us at school.',
                    'I can say where things go in my classroom.',
                ],
                'notes': (
                    '<p>This is my <strong>classroom</strong>.</p>'
                    '<ul><li>We sit at desks and on the mat.</li>'
                    '<li>Our bags go in the same place every day.</li>'
                    '<li>Books go on the shelf.</li></ul>'
                    '<p>People who help us at school: the <strong>teacher</strong>, the '
                    '<strong>principal</strong>, the <strong>secretary</strong> in the office, and the '
                    '<strong>cleaners</strong> and <strong>gardeners</strong>.</p>'
                ),
                'key_terms': [('classroom', 'the room where we learn'),
                              ('principal', 'the head of the school')],
                'example': {'title': 'Class activity: classroom tour', 'html': (
                    '<p>Walk around the classroom with the teacher.</p>'
                    '<ol><li>Find the mat, the bookshelf and the bin.</li>'
                    '<li>Find where your bag goes.</li>'
                    '<li>Find where we wash our hands or the closest toilet.</li></ol>'
                    '<p>Point and say: "This is the ...".</p>')},
                'video': {'id': 'AKnUdOnsMWs',
                          'title': 'My Classroom |  🍎 Back to School Anthem for Preschool | Super Simple Songs',
                          'channel': 'Super Simple Songs - Kids Songs', 'minutes': 3},
                'worksheet': {'instructions': 'Draw and colour.',
                              'exercises': [
                                  'Draw your classroom.',
                                  'Draw your teacher.',
                                  'Draw where you put your bag.',
                                  'Circle what we find in a classroom: desk / bath / book / bed',
                              ]},
                'quiz': [
                    ('mcq', 'Who is the head of the school?', ['the principal', 'a learner', 'a parent'], 0),
                    ('tf', 'Books go on the shelf.', True),
                    ('mcq', 'What do we find in a classroom?', ['a stove', 'a desk', 'a bed'], 1),
                ],
                'homework': {'title': 'Tell me about school',
                             'instructions': 'Talk to your family about your school.',
                             'tasks': ['Tell your family 3 things that are in your classroom.',
                                       'Tell them the name of your teacher.'],
                             'marks': 5},
            },
            {
                'title': 'School rules keep us safe',
                'minutes': 30,
                'objectives': [
                    'I can say some school rules.',
                    'I can say why we have rules.',
                ],
                'notes': (
                    '<p><strong>Rules</strong> help us to be safe and kind.</p>'
                    '<ul><li>Walk in the classroom. Do not run.</li>'
                    '<li>Put up your hand to talk.</li><li>Listen when others talk.</li>'
                    '<li>Share and take turns.</li><li>Stay inside the school gate.</li>'
                    '<li>Tell a teacher if you are hurt or scared.</li></ul>'
                ),
                'key_terms': [('rule', 'something we all agree to do'),
                              ('safe', 'not in danger, not hurt')],
                'example': {'title': 'Class activity: thumbs up, thumbs down', 'html': (
                    '<p>The teacher says what a child does. Is it following the rules?</p>'
                    '<ul><li>Thabo runs in the classroom. (Thumbs down)</li>'
                    '<li>Aisha puts up her hand. (Thumbs up)</li>'
                    '<li>Ben shares the crayons. (Thumbs up)</li></ul>')},
                'video': {'id': 'iQxK-Ah7has',
                          'title': 'I Can Follow the Rules | Learn the Rules | Learning Song for Kids | Preschool & Kindergarten',
                          'channel': 'HeidiSongs', 'minutes': 3},
                'worksheet': {'instructions': 'Tick the good choices. Cross the bad choices.',
                              'exercises': [
                                  'I walk in the classroom.  ( )',
                                  'I push my friend.  ( )',
                                  'I put up my hand.  ( )',
                                  'I share my crayons.  ( )',
                                  'Draw yourself following a rule.',
                              ]},
                'quiz': [
                    ('tf', 'We run in the classroom.', False),
                    ('mcq', 'What do we do when we want to talk?', ['Shout', 'Put up our hand', 'Stand on a chair'], 1),
                    ('mcq', 'Why do we have rules?', ['To keep us safe', 'To make us sad', 'To stop us playing'], 0),
                ],
                'homework': {'title': 'Rules at home',
                             'instructions': 'Talk with a grown-up about rules at home.',
                             'tasks': ['Ask a grown-up to tell you one rule at home.',
                                       'Draw a picture of that rule.'],
                             'marks': 5},
            },
            {
                'title': 'Moving safely in our space (PE and Creative Arts)',
                'minutes': 30,
                'objectives': [
                    'I can move without bumping into others.',
                    'I can stop and freeze when I hear the signal.',
                    'I can move in different ways: walk, hop, skip.',
                ],
                'notes': (
                    '<p>When we play, we find our own <strong>space</strong>.</p>'
                    '<ul><li>Stretch out your arms. Nobody should be inside your space.</li>'
                    '<li>Look where you are going.</li>'
                    '<li>When the music stops, <strong>freeze</strong> like a statue!</li></ul>'
                    '<p>Ways to move: walk, march, hop, jump, skip, tiptoe.</p>'
                    '<p>Drink water after you play.</p>'
                ),
                'key_terms': [('space', 'the area around your body'),
                              ('freeze', 'stop and stay very still')],
                'example': {'title': 'Class activity: freeze dance', 'html': (
                    '<ol><li>Find your own space outside or in the hall.</li>'
                    '<li>Move to the music. The teacher says how: hop, tiptoe, march.</li>'
                    '<li>When the music stops, freeze!</li>'
                    '<li>Cool down: stretch up tall, then curl up small.</li></ol>')},
                'video': {'id': 'A1vdKfXlB_g', 'title': 'The Dance Freeze Song | Freeze Dance | Scratch Garden',
                          'channel': 'Scratch Garden', 'minutes': 3},
                'worksheet': {'instructions': 'Draw yourself moving.',
                              'exercises': [
                                  'Draw yourself hopping.',
                                  'Draw yourself frozen like a statue.',
                                  'Draw what you drink after playing.',
                                  'Circle the safe one: running into friends / looking where I go',
                              ]},
                'quiz': [
                    ('mcq', 'What do we do when the music stops?', ['Run', 'Shout', 'Freeze'], 2),
                    ('tf', 'We look where we are going when we move.', True),
                    ('mcq', 'Which is a way to move?', ['hop', 'sleep', 'read'], 0),
                ],
                'homework': {'title': 'Move at home',
                             'instructions': 'Play a moving game with your family.',
                             'tasks': ['Play freeze dance at home with a song.',
                                       'Show a grown-up 3 ways you can move.'],
                             'marks': 5},
            },
        ],
    },

    (2, 'LIFE-SK'): {
        'topic': 'All about me',
        'caps': 'Personal and Social Well-being and Beginning Knowledge: Me (I am special, my '
                'likes and dislikes, my feelings); Creative Arts: self-portrait; Physical Education: '
                'what my body can do (Gr 2 Term 1 ATP)',
        'summary': 'Learners talk about what makes them special, name and handle feelings, '
                   'and explore what their bodies can do through movement and a self-portrait.',
        'days': [
            {
                'title': 'I am special',
                'minutes': 30,
                'objectives': [
                    'I can tell others about myself.',
                    'I can say what I like and what I can do.',
                    'I can say that everyone is special.',
                ],
                'notes': (
                    '<p>There is only one <strong>you</strong>!</p>'
                    '<ul><li>You have your own name.</li><li>You have your own face and voice.</li>'
                    '<li>You like some things and not others.</li>'
                    '<li>You are good at some things.</li></ul>'
                    '<p>Everybody is <strong>special</strong>. We are different, and that is good. '
                    'We are kind to everyone.</p>'
                ),
                'key_terms': [('special', 'there is nobody else just like you'),
                              ('different', 'not the same')],
                'example': {'title': 'Class activity: me cards', 'html': (
                    '<p>Each child finishes these sentences out loud:</p>'
                    '<ul><li>My name is ...</li><li>I like ...</li><li>I am good at ...</li></ul>'
                    '<p>Find a friend who likes the same thing as you, and one who likes something different.</p>')},
                'video': {'id': 'rhsGJXzEfsM',
                          'title': 'I Am Special  -  Preschool Songs & Nursery Rhymes for an All About Me Theme',
                          'channel': 'The Kiboomers - Kids Music Channel', 'minutes': 2},
                'worksheet': {'instructions': 'Fill in and draw.',
                              'exercises': [
                                  'My name is __________.',
                                  'I am ____ years old.',
                                  'My favourite food is __________.',
                                  'I am good at __________.',
                                  'Draw something you like to do.',
                              ]},
                'quiz': [
                    ('tf', 'Everybody is special.', True),
                    ('mcq', 'Are all people the same?', ['Yes', 'No, we are different', 'Only children are'], 1),
                    ('mcq', 'How do we treat people who are different from us?',
                     ['We are kind', 'We laugh at them', 'We ignore them'], 0),
                ],
                'homework': {'title': 'My special box',
                             'instructions': 'Talk with a grown-up about you.',
                             'tasks': ['Ask a grown-up: "What is special about me?"',
                                       'Draw 3 things that are special about you.'],
                             'marks': 6},
            },
            {
                'title': 'My feelings',
                'minutes': 30,
                'objectives': [
                    'I can name feelings: happy, sad, angry, scared.',
                    'I can show a feeling on my face.',
                    'I can say what to do when I have a big feeling.',
                ],
                'notes': (
                    '<p>We all have <strong>feelings</strong>.</p>'
                    '<ul><li><strong>Happy</strong> - I smile.</li><li><strong>Sad</strong> - I may cry.</li>'
                    '<li><strong>Angry</strong> - my face goes hot and tight.</li>'
                    '<li><strong>Scared</strong> - my heart beats fast.</li></ul>'
                    '<p>All feelings are OK. When a feeling is big:</p>'
                    '<ul><li>Take 3 slow breaths.</li><li>Talk to a grown-up you trust.</li></ul>'
                ),
                'key_terms': [('feelings', 'how we feel inside, like happy or sad')],
                'example': {'title': 'Class activity: feelings faces', 'html': (
                    '<p>The teacher reads a story sentence. Show the feeling on your face.</p>'
                    '<ul><li>"It is my birthday!" (happy)</li><li>"My ice cream fell." (sad)</li>'
                    '<li>"Someone took my toy." (angry)</li><li>"There is a loud storm." (scared)</li></ul>'
                    '<p>Then practise "smell the flower, blow out the candle" breathing.</p>')},
                'video': {'id': 'KivttwaXQZ4', 'title': 'Feelings Song | Emotions Song | The Singing Walrus',
                          'channel': 'The Singing Walrus - English Songs For Kids', 'minutes': 3},
                'worksheet': {'instructions': 'Draw the faces and finish the sentences.',
                              'exercises': [
                                  'Draw a happy face.',
                                  'Draw a sad face.',
                                  'I feel happy when __________.',
                                  'I feel scared when __________.',
                                  'When I am angry I can __________.',
                              ]},
                'quiz': [
                    ('mcq', 'You get a present. How do you feel?', ['sad', 'scared', 'happy'], 2),
                    ('tf', 'All feelings are OK.', True),
                    ('mcq', 'What can you do when you feel very angry?',
                     ['Take slow breaths', 'Hit someone', 'Break something'], 0),
                ],
                'homework': {'title': 'Feelings at home',
                             'instructions': 'Talk about feelings with a grown-up.',
                             'tasks': ['Ask a grown-up what makes them happy.',
                                       'Show your grown-up the slow-breathing trick.',
                                       'Draw a time you felt happy.'],
                             'marks': 6},
            },
            {
                'title': 'What my body can do: self-portrait and movement',
                'minutes': 30,
                'objectives': [
                    'I can name the main parts of my body.',
                    'I can move different body parts.',
                    'I can draw a picture of myself.',
                ],
                'notes': (
                    '<p>My body can do many things!</p>'
                    '<ul><li>My <strong>legs</strong> help me run and jump.</li>'
                    '<li>My <strong>arms and hands</strong> help me throw, catch and draw.</li>'
                    '<li>My <strong>eyes</strong> see, my <strong>ears</strong> hear.</li></ul>'
                    '<p>A <strong>self-portrait</strong> is a picture you draw of yourself. '
                    'Look in a mirror. What colour are your eyes? Is your hair long or short?</p>'
                ),
                'key_terms': [('self-portrait', 'a picture of yourself that you make')],
                'example': {'title': 'Class activity: body warm-up, then draw', 'html': (
                    '<ol><li>Warm up: nod your head, roll your shoulders, wiggle your fingers, march your legs.</li>'
                    '<li>Throw and catch a bean bag with a partner.</li>'
                    '<li>Back in class: look in a mirror and draw your face. Add your eyes, nose, mouth, ears and hair.</li></ol>')},
                'video': {'id': '0Trlt67kKE4', 'title': 'My Body | Parts of the Body for Kids! | Jack Hartmann',
                          'channel': 'Jack Hartmann Kids Music Channel', 'minutes': 4},
                'worksheet': {'instructions': 'Draw your self-portrait and answer.',
                              'exercises': [
                                  'Draw yourself in the frame.',
                                  'I use my ________ to run.',
                                  'I use my ________ to see.',
                                  'I use my ________ to catch a ball.',
                                  'One thing my body can do well: __________.',
                              ]},
                'quiz': [
                    ('mcq', 'What do we use to hear?', ['eyes', 'ears', 'feet'], 1),
                    ('mcq', 'A self-portrait is ...', ['a picture of yourself', 'a picture of a tree', 'a song'], 0),
                    ('tf', 'We use our legs to jump.', True),
                ],
                'homework': {'title': 'Body moves',
                             'instructions': 'Have fun moving with your family.',
                             'tasks': ['Play catch with a ball or rolled-up socks for 10 minutes.',
                                       'Ask a grown-up to help you trace around your hand and colour it.'],
                             'marks': 5},
            },
        ],
    },

    (3, 'LIFE-SK'): {
        'topic': 'My body and healthy habits',
        'caps': 'Beginning Knowledge and Personal and Social Well-being: My body (growing and '
                'changing), keeping clean and healthy, healthy food; Physical Education: '
                'locomotor movement and fitness (Gr 3 Term 1 ATP)',
        'summary': 'Learners explore how their bodies grow, practise hygiene habits such as hand '
                   'washing, and learn about healthy food and exercise.',
        'days': [
            {
                'title': 'My body grows and changes',
                'minutes': 30,
                'objectives': [
                    'I can describe how I have grown since I was a baby.',
                    'I can say what my body needs to grow.',
                ],
                'notes': (
                    '<p>When you were a <strong>baby</strong>, you could not walk or talk. Now you can run, read and write!</p>'
                    '<ul><li>Our bones get longer, so we grow taller.</li>'
                    '<li>Our feet grow, so we need bigger shoes.</li>'
                    '<li>We lose our milk teeth and get adult teeth.</li></ul>'
                    '<p>To grow well, our bodies need <strong>food, water, sleep, exercise</strong> and love and care.</p>'
                ),
                'key_terms': [('grow', 'get bigger'), ('milk teeth', 'the first teeth, which fall out')],
                'example': {'title': 'Class activity: then and now', 'html': (
                    '<p>Make a table on the board:</p>'
                    '<ul><li>As a baby I ... (drank milk, crawled, slept a lot)</li>'
                    '<li>Now I ... (eat many foods, run, read)</li></ul>'
                    '<p>Measure two learners with a string. Who is taller? Everyone grows at their own speed.</p>')},
                'video': {'id': 'raHFnQz82bs', 'title': 'Science for Kids: How Do Our Bodies Grow? | The Wonder Why Lab',
                          'channel': 'The Wonder Why Lab', 'minutes': 5},
                'worksheet': {'instructions': 'Answer the questions.',
                              'exercises': [
                                  'When I was a baby I could __________.',
                                  'Now I can __________.',
                                  'Name 3 things your body needs to grow.',
                                  'Have you lost a milk tooth? How many? ____',
                                  'Draw yourself as a baby and as you are now.',
                              ]},
                'quiz': [
                    ('mcq', 'What helps our bodies grow?', ['sleep and good food', 'sweets only', 'staying up late'], 0),
                    ('tf', 'Everyone grows at exactly the same speed.', False),
                    ('mcq', 'The first teeth that fall out are called ...', ['adult teeth', 'milk teeth', 'gold teeth'], 1),
                    ('tf', 'Our feet grow, so we need bigger shoes.', True),
                ],
                'homework': {'title': 'Baby me',
                             'instructions': 'Ask a grown-up about when you were a baby.',
                             'tasks': ['Ask: "What could I do when I was one year old?"',
                                       'Ask a grown-up to measure your height with a string or tape. Bring the string to school.',
                                       'Write 2 sentences about how you have changed.'],
                             'marks': 10},
            },
            {
                'title': 'Keeping clean: washing hands and hygiene',
                'minutes': 30,
                'objectives': [
                    'I can wash my hands the right way.',
                    'I can say when to wash my hands.',
                    'I can name other ways to keep clean.',
                ],
                'notes': (
                    '<p><strong>Germs</strong> are tiny living things that can make us sick. We cannot see them.</p>'
                    '<p>Wash your hands with soap and water:</p>'
                    '<ol><li>Wet your hands.</li><li>Rub with soap: palms, backs, between fingers, nails.</li>'
                    '<li>Scrub for 20 seconds (sing "Happy Birthday" twice).</li>'
                    '<li>Rinse and dry.</li></ol>'
                    '<p>Wash before eating, after the toilet, and after playing outside. '
                    'Also brush your teeth twice a day and bath or wash every day.</p>'
                ),
                'key_terms': [('germs', 'tiny living things that can make us sick'),
                              ('hygiene', 'keeping ourselves clean to stay healthy')],
                'example': {'title': 'Class activity: glitter germs', 'html': (
                    '<p>Put a little glitter or flour on one child\'s hands. They shake hands with 3 friends.</p>'
                    '<p>Look: the "germs" spread! Now wash with only water, then with soap. '
                    'Soap works best.</p>')},
                'video': {'id': 'evXG5HuwIn0',
                          'title': "Wash your hands Children's Song | Wash us - Healthy habits Song | Hooray Kids Songs & Nursery Rhymes",
                          'channel': 'Hooray Kids Songs & Nursery Rhymes', 'minutes': 3},
                'worksheet': {'instructions': 'Answer and number the steps.',
                              'exercises': [
                                  'Number the steps 1-4: Rinse ( )  Wet hands ( )  Dry ( )  Rub with soap ( )',
                                  'Name 2 times you must wash your hands.',
                                  'How long should you scrub your hands? ______',
                                  'How many times a day should you brush your teeth? ____',
                                  'Draw yourself keeping clean.',
                              ]},
                'quiz': [
                    ('mcq', 'When must you wash your hands?', ['after using the toilet', 'only on Sundays', 'never'], 0),
                    ('mcq', 'How long should you scrub with soap?', ['2 seconds', 'about 20 seconds', '1 hour'], 1),
                    ('tf', 'We can see germs with our eyes.', False),
                    ('mcq', 'What helps wash away germs best?', ['water only', 'a towel only', 'soap and water'], 2),
                ],
                'homework': {'title': 'Clean hands chart',
                             'instructions': 'Show your family how to wash hands properly.',
                             'tasks': ['Teach a grown-up the 4 hand-washing steps.',
                                       'Tick each time you wash your hands before eating this week.',
                                       'Make a small poster: "Wash your hands!"'],
                             'marks': 10},
            },
            {
                'title': 'Healthy food and exercise',
                'minutes': 30,
                'objectives': [
                    'I can sort foods into healthy and "sometimes" foods.',
                    'I can say why exercise is good for me.',
                    'I can do a simple fitness circuit.',
                ],
                'notes': (
                    '<p><strong>Healthy food</strong> gives us energy and helps us grow.</p>'
                    '<ul><li>Eat fruit and vegetables every day.</li>'
                    '<li>Eat foods like pap, bread, beans, eggs, fish, chicken and milk.</li>'
                    '<li>Drink clean water.</li>'
                    '<li>Sweets, chips and fizzy drinks are <em>sometimes</em> foods.</li></ul>'
                    '<p><strong>Exercise</strong> makes our heart and muscles strong. '
                    'Play actively for at least an hour every day.</p>'
                ),
                'key_terms': [('healthy', 'good for your body'),
                              ('exercise', 'moving your body to keep fit')],
                'example': {'title': 'Class activity: lunchbox sort and fitness circuit', 'html': (
                    '<p>Sort food pictures into two groups: <strong>every day</strong> (apple, carrot, '
                    'brown bread, egg, water) and <strong>sometimes</strong> (sweets, chips, cool drink).</p>'
                    '<p>Then do a circuit outside, 30 seconds each: star jumps, running on the spot, '
                    'hopping, frog jumps. Feel your heart beat faster!</p>')},
                'video': {'id': '5dR22hbln6w', 'title': 'Good Foods | Healthy Foods Song for Kids | Jack Hartmann',
                          'channel': 'Jack Hartmann Kids Music Channel', 'minutes': 4},
                'worksheet': {'instructions': 'Sort the foods and plan a healthy lunchbox.',
                              'exercises': [
                                  'Write E (every day) or S (sometimes): apple ( ) sweets ( ) carrot ( ) chips ( )',
                                  'Write E or S: water ( ) fizzy drink ( ) egg ( ) beans ( )',
                                  'Draw a healthy lunchbox with 4 foods.',
                                  'Name 2 ways you can exercise.',
                                  'Why is exercise good for you?',
                              ]},
                'quiz': [
                    ('mcq', 'Which is a healthy everyday food?', ['sweets', 'chips', 'an apple'], 2),
                    ('tf', 'Exercise makes our heart stronger.', True),
                    ('mcq', 'What is the best drink for your body?', ['water', 'fizzy drink', 'sweet juice only'], 0),
                    ('tf', 'We should eat sweets every day.', False),
                ],
                'homework': {'title': 'Healthy family plan',
                             'instructions': 'Plan with a grown-up.',
                             'tasks': ['Help a grown-up pack or plan a healthy lunchbox.',
                                       'Do 10 minutes of exercise with your family (skipping, dancing or a walk).',
                                       'Draw what you ate for supper and say if it was healthy.'],
                             'marks': 10},
            },
        ],
    },

    # ------------------------------------------------------------------ CODING AND ROBOTICS
    (1, 'CODING'): {
        'topic': 'Patterns, sequences and giving instructions',
        'caps': 'Pattern Recognition: identify, copy and extend repeating patterns; Algorithms and '
                'Coding: sequence steps of a familiar activity; give and follow simple directional '
                'instructions, unplugged (DBE draft CAPS Coding and Robotics Gr 1, Term 1)',
        'summary': 'Learners copy and extend simple repeating patterns, put the steps of daily '
                   'activities in order, and give and follow movement instructions like a robot.',
        'days': [
            {
                'title': 'Repeating patterns',
                'minutes': 30,
                'objectives': [
                    'I can see a pattern that repeats.',
                    'I can copy a pattern.',
                    'I can say what comes next.',
                ],
                'notes': (
                    '<p>A <strong>pattern</strong> repeats again and again.</p>'
                    '<p>red, blue, red, blue, red, blue ...</p>'
                    '<ul><li>Find the part that repeats.</li><li>Say it out loud.</li>'
                    '<li>Say what comes next.</li></ul>'
                    '<p>We can make patterns with colours, shapes, sounds and moves: clap, stamp, clap, stamp.</p>'
                    '<p>Computers and robots use patterns too!</p>'
                ),
                'key_terms': [('pattern', 'something that repeats in the same way')],
                'example': {'title': 'Class activity: body patterns', 'html': (
                    '<p>Do this pattern with the teacher: <strong>clap, clap, stamp</strong>, clap, clap, stamp ...</p>'
                    '<p>What comes next? (clap)</p>'
                    '<p>Now make a pattern with children: stand, sit, stand, sit. Who comes next?</p>')},
                'video': {'id': 'Js45cR_7wFE', 'title': 'Patterns! | Mini Math Movies | Scratch Garden',
                          'channel': 'Scratch Garden', 'minutes': 4},
                'worksheet': {'instructions': 'What comes next? Draw or write it.',
                              'exercises': [
                                  'O X O X O X ___',
                                  'red, yellow, red, yellow, ___',
                                  'circle, square, circle, square, ___',
                                  'clap, stamp, clap, stamp, ___',
                                  'A A B A A B A A ___',
                                  'Colour your own pattern of 6 beads.',
                              ]},
                'quiz': [
                    ('mcq', 'What comes next? O X O X O ...', ['O', 'X', 'Z'], 1),
                    ('mcq', 'What comes next? red, blue, red, blue ...', ['red', 'green', 'blue'], 0),
                    ('tf', 'A pattern repeats in the same way.', True),
                ],
                'homework': {'title': 'Pattern hunt',
                             'instructions': 'Look for patterns at home with a grown-up.',
                             'tasks': ['Find a pattern on clothes, a blanket or tiles.',
                                       'Make a pattern with spoons and forks: spoon, fork, spoon, fork.'],
                             'marks': 5},
            },
            {
                'title': 'Steps in order: first, next, last',
                'minutes': 30,
                'objectives': [
                    'I can put steps in the right order.',
                    'I can use the words first, next and last.',
                ],
                'notes': (
                    '<p>Many jobs have <strong>steps</strong>. The steps must be in the right <strong>order</strong>.</p>'
                    '<p>Brushing teeth:</p>'
                    '<ol><li><strong>First</strong>, put toothpaste on the brush.</li>'
                    '<li><strong>Next</strong>, brush your teeth.</li>'
                    '<li><strong>Last</strong>, rinse your mouth.</li></ol>'
                    '<p>If the order is wrong, it does not work! Robots also need steps in the right order.</p>'
                ),
                'key_terms': [('steps', 'the small parts of a job'),
                              ('order', 'which step comes first, next and last')],
                'example': {'title': 'Class activity: picture cards', 'html': (
                    '<p>The teacher shows 3 mixed-up pictures: putting on shoes, putting on socks, tying laces.</p>'
                    '<ol><li>Which comes first? (socks)</li><li>Next? (shoes)</li><li>Last? (tie laces)</li></ol>'
                    '<p>Act out the steps in order.</p>')},
                'video': {'id': 'GHspjqQPPkk', 'title': "Leo's Day Planner: First, Next, Last | Preschool Math",
                          'channel': 'Leo the Little Lion – Stories & Learning', 'minutes': 4},
                'worksheet': {'instructions': 'Write 1, 2 and 3 to put the steps in order.',
                              'exercises': [
                                  'Eat the banana ( )  Peel the banana ( )  Pick up the banana ( )',
                                  'Dry your hands ( )  Wet your hands ( )  Use soap ( )',
                                  'Get into bed ( )  Put on pyjamas ( )  Close your eyes ( )',
                                  'Draw 3 steps to make a sandwich.',
                              ]},
                'quiz': [
                    ('mcq', 'What do you do FIRST to put on shoes?', ['tie the laces', 'put on socks', 'walk'], 1),
                    ('tf', 'The order of steps does not matter.', False),
                    ('mcq', 'Which word tells us the end?', ['first', 'next', 'last'], 2),
                ],
                'homework': {'title': 'Steps at home',
                             'instructions': 'Do a job with a grown-up and talk about the steps.',
                             'tasks': ['Help make tea or a sandwich. Say "first, next, last" for each step.',
                                       'Draw the 3 steps.'],
                             'marks': 5},
            },
            {
                'title': 'Robot game: giving instructions',
                'minutes': 30,
                'objectives': [
                    'I can give clear instructions: forward, turn left, turn right, stop.',
                    'I can follow instructions like a robot.',
                    'I can know my left hand and right hand.',
                ],
                'notes': (
                    '<p>A <strong>robot</strong> is a machine. It only does what we tell it.</p>'
                    '<p>We give a robot <strong>instructions</strong>:</p>'
                    '<ul><li><strong>Step forward</strong></li><li><strong>Turn left</strong></li>'
                    '<li><strong>Turn right</strong></li><li><strong>Stop</strong></li></ul>'
                    '<p>Your writing hand is often your right hand. Hold up your left hand: '
                    'the thumb and finger make an <strong>L</strong>.</p>'
                ),
                'key_terms': [('robot', 'a machine that follows instructions'),
                              ('instruction', 'telling someone exactly what to do')],
                'example': {'title': 'Class game: teacher robot', 'html': (
                    '<p>The teacher is the robot. The class must get the robot to the door.</p>'
                    '<ol><li>Class: "Step forward, step forward."</li><li>Class: "Turn right."</li>'
                    '<li>Class: "Step forward ... Stop!"</li></ol>'
                    '<p>If the robot goes the wrong way, change the instructions and try again.</p>')},
                'video': {'id': 'gRbwFq9665k', 'title': 'The Left vs. Right Song! | Scratch Garden',
                          'channel': 'Scratch Garden', 'minutes': 3},
                'worksheet': {'instructions': 'Follow the instructions. Your teacher will read them.',
                              'exercises': [
                                  'Colour your LEFT hand outline red.',
                                  'Colour your RIGHT hand outline blue.',
                                  'Draw a robot.',
                                  'Write the robot words: forward, left, right, stop.',
                                  'Draw a path from the robot to a ball.',
                              ]},
                'quiz': [
                    ('mcq', 'A robot does ...', ['what we tell it', 'whatever it wants', 'nothing ever'], 0),
                    ('mcq', 'Which is a robot instruction?', ['Be happy', 'Turn left', 'Think hard'], 1),
                    ('tf', 'Your left thumb and finger can make the letter L.', True),
                ],
                'homework': {'title': 'Be a robot',
                             'instructions': 'Play the robot game with a grown-up.',
                             'tasks': ['Give a grown-up instructions to walk from the door to a chair.',
                                       'Now let them give you instructions. You are the robot!'],
                             'marks': 5},
            },
        ],
    },

    (2, 'CODING'): {
        'topic': 'Patterns, algorithms and unplugged coding',
        'caps': 'Pattern Recognition: identify the rule in repeating and growing patterns; '
                'Algorithms and Coding: write a simple algorithm for a real-life task; unplugged '
                'coding on a grid using direction symbols (DBE draft CAPS Coding and Robotics Gr 2, Term 1)',
        'summary': 'Learners find the rule in patterns, write algorithms (step-by-step instructions) '
                   'for everyday tasks, and code a path on a grid using direction commands.',
        'days': [
            {
                'title': 'Finding the rule in a pattern',
                'minutes': 30,
                'objectives': [
                    'I can find the part of a pattern that repeats.',
                    'I can say the rule of a pattern.',
                    'I can find a mistake in a pattern.',
                ],
                'notes': (
                    '<p>Every pattern has a <strong>rule</strong>.</p>'
                    '<ul><li>Repeating: A B B, A B B, A B B. The rule: one A, then two B\'s.</li>'
                    '<li>Growing: 1 block, 2 blocks, 3 blocks. The rule: add one each time.</li></ul>'
                    '<p>If you know the rule, you can say what comes next, and you can spot a mistake.</p>'
                    '<p>Coders look for patterns so they can solve problems faster.</p>'
                ),
                'key_terms': [('rule', 'what a pattern does every time'),
                              ('repeating pattern', 'a pattern where the same part comes again'),
                              ('growing pattern', 'a pattern that gets bigger by the same amount')],
                'example': {'title': 'Worked example: spot the mistake', 'html': (
                    '<p>Look: <strong>circle, star, star, circle, star, circle, star, star</strong></p>'
                    '<ol><li>The part that repeats is: circle, star, star.</li>'
                    '<li>Check each group: circle star star / circle star <em>circle</em> ...</li>'
                    '<li>The 6th shape should be a <strong>star</strong>, not a circle.</li></ol>')},
                'video': {'id': 'MBjjxSx45-Q', 'title': 'The Patterns Practice Song | Math Songs | Scratch Garden',
                          'channel': 'Scratch Garden', 'minutes': 3},
                'worksheet': {'instructions': 'Write the rule and what comes next.',
                              'exercises': [
                                  'A B B A B B A ___ ___',
                                  'jump, clap, clap, jump, clap, clap, ___',
                                  '2, 4, 6, 8, ___ (rule: ______)',
                                  'Find the mistake: X O X O O X O',
                                  '* , ** , *** , ____',
                                  'Make your own pattern and write its rule.',
                              ]},
                'quiz': [
                    ('mcq', 'What comes next? A B B A B B A ...', ['A', 'B', 'C'], 1),
                    ('mcq', 'What is the rule? 1, 2, 3, 4, 5', ['add one', 'add two', 'take away one'], 0),
                    ('tf', 'A growing pattern gets bigger each time.', True),
                    ('mcq', 'Which pattern has a mistake?', ['X O X O', 'red blue red blue', 'X O O O X O'], 2),
                ],
                'homework': {'title': 'Pattern maker',
                             'instructions': 'Make patterns with things at home.',
                             'tasks': ['Use pegs, buttons or pasta to make a repeating pattern. Tell a grown-up the rule.',
                                       'Make a growing pattern with spoons: 1, 2, 3, 4.',
                                       'Draw both patterns.'],
                             'marks': 10},
            },
            {
                'title': 'What is an algorithm?',
                'minutes': 30,
                'objectives': [
                    'I can say what an algorithm is.',
                    'I can write clear steps for a task.',
                    'I can test steps to see if they work.',
                ],
                'notes': (
                    '<p>An <strong>algorithm</strong> is a list of steps to do a job, in the right order.</p>'
                    '<p>Making a jam sandwich:</p>'
                    '<ol><li>Take two slices of bread.</li><li>Open the jam.</li>'
                    '<li>Spread jam on one slice with a knife.</li>'
                    '<li>Put the other slice on top.</li></ol>'
                    '<p>Steps must be <strong>clear</strong> and in <strong>order</strong>. '
                    'A computer cannot guess what you mean!</p>'
                ),
                'key_terms': [('algorithm', 'step-by-step instructions to do a job')],
                'example': {'title': 'Class activity: the silly robot', 'html': (
                    '<p>The teacher acts as a robot that does <em>exactly</em> what it hears.</p>'
                    '<p>A learner says: "Put jam on the bread." The robot puts the closed jar on the bread!</p>'
                    '<p>Fix the algorithm: "Open the jar. Pick up the knife. Put jam on the knife. Spread it on the bread."</p>')},
                'video': {'id': '578hB0E6y4o',
                          'title': '🖥 What are Algorithms? | Computer Science for Kids Part 5 | Grades K-2',
                          'channel': "Ms. Dorismond's Virtual Corner", 'minutes': 5},
                'worksheet': {'instructions': 'Number the steps of each algorithm in order.',
                              'exercises': [
                                  'Planting a seed: Water it ( )  Dig a hole ( )  Put in the seed ( )  Cover with soil ( )',
                                  'Brushing teeth: Rinse ( )  Brush ( )  Put on toothpaste ( )',
                                  'Write an algorithm with 4 steps for putting on a jersey.',
                                  'Which step is not clear? "Do the thing, then finish." Rewrite it.',
                              ]},
                'quiz': [
                    ('mcq', 'An algorithm is ...', ['a type of animal', 'a list of steps in order', 'a song'], 1),
                    ('tf', 'A computer can guess what you mean if your steps are not clear.', False),
                    ('mcq', 'What is the first step to make tea?', ['Drink the tea', 'Add milk', 'Boil the water'], 2),
                ],
                'homework': {'title': 'My home algorithm',
                             'instructions': 'Write an algorithm for a job at home. Let a grown-up test it.',
                             'tasks': ['Write 4 to 6 steps for a job (e.g. making your bed).',
                                       'Ask a grown-up to follow your steps exactly. Did it work?',
                                       'Fix any step that was not clear.'],
                             'marks': 10},
            },
            {
                'title': 'Unplugged coding on a grid',
                'minutes': 30,
                'objectives': [
                    'I can use direction commands to move on a grid.',
                    'I can write a code to get from start to finish.',
                ],
                'notes': (
                    '<p>We can <strong>code</strong> a path on a grid using commands.</p>'
                    '<ul><li><strong>U</strong> = move up one square</li>'
                    '<li><strong>D</strong> = move down one square</li>'
                    '<li><strong>L</strong> = move left one square</li>'
                    '<li><strong>R</strong> = move right one square</li></ul>'
                    '<p>Example: R R D means right, right, down.</p>'
                    '<p>A <strong>code</strong> is an algorithm written in a language a robot or computer understands.</p>'
                ),
                'key_terms': [('code', 'instructions a computer or robot can follow'),
                              ('grid', 'squares in rows and columns')],
                'example': {'title': 'Class activity: Happy Maps', 'html': (
                    '<p>Draw a 4 by 4 grid on the floor with chalk or tape. Put a "robot" child on the start square '
                    'and a ball 2 squares right and 1 square down.</p>'
                    '<ol><li>Write the code on the board: R R D.</li>'
                    '<li>The robot follows the code, one command at a time.</li>'
                    '<li>Did the robot reach the ball? Try a different code that also works: D R R.</li></ol>')},
                'video': {'id': 'hrnhiKAQ1_k', 'title': 'Unplugged - Happy Maps',
                          'channel': 'CodeAI', 'minutes': 4},
                'worksheet': {'instructions': 'Use U, D, L and R. Draw a 5 by 5 grid to help you.',
                              'exercises': [
                                  'Start at the top left. Follow R R R. Where are you? Mark it.',
                                  'Start at the top left. Follow D D R. Mark where you end.',
                                  'Write the code to move 2 squares right and 2 squares down.',
                                  'What does L L U mean?',
                                  'Draw a cat and a fish on your grid. Write the code to get the cat to the fish.',
                              ]},
                'quiz': [
                    ('mcq', 'What does R mean?', ['move right', 'move left', 'run'], 0),
                    ('mcq', 'Which code moves 2 squares down?', ['U U', 'R R', 'D D'], 2),
                    ('tf', 'There can be more than one code to get to the same square.', True),
                ],
                'homework': {'title': 'Code a path at home',
                             'instructions': 'Make a grid on paper or with tiles at home.',
                             'tasks': ['Put a toy at the start and a sweet or toy at the finish.',
                                       'Write the code using U, D, L, R.',
                                       'Ask a grown-up to follow your code with the toy.'],
                             'marks': 10},
            },
        ],
    },

    (3, 'CODING'): {
        'topic': 'Algorithms, coding sequences and debugging',
        'caps': 'Algorithms and Coding: write and follow algorithms for real-life tasks; code '
                'sequences with symbols (unplugged); find and fix errors (debugging) '
                '(DBE draft CAPS Coding and Robotics Gr 3, Term 1)',
        'summary': 'Learners write precise algorithms for real-life tasks, code a partner with '
                   'symbol programs, and learn to debug instructions that do not work.',
        'days': [
            {
                'title': 'Real-life algorithms',
                'minutes': 35,
                'objectives': [
                    'I can explain what an algorithm is.',
                    'I can write a precise algorithm for a real-life task.',
                    'I can tell why order and detail matter.',
                ],
                'notes': (
                    '<p>An <strong>algorithm</strong> is a precise, step-by-step set of instructions to '
                    'complete a task.</p>'
                    '<ul><li>Each step must be <strong>clear</strong> (only one meaning).</li>'
                    '<li>Steps must be in the right <strong>order</strong>.</li>'
                    '<li>It must have a <strong>start</strong> and an <strong>end</strong>.</li></ul>'
                    '<p>We use algorithms every day: getting ready for school, planting a seed, '
                    'following a recipe. Computers follow algorithms written as code.</p>'
                ),
                'key_terms': [('algorithm', 'a precise list of steps to complete a task'),
                              ('precise', 'exact and clear')],
                'example': {'title': 'Worked example: plant a seed', 'html': (
                    '<ol><li>Fill a cup with soil.</li><li>Make a hole with your finger.</li>'
                    '<li>Put one seed in the hole.</li><li>Cover the seed with soil.</li>'
                    '<li>Water it a little.</li><li>Put it in a sunny place.</li></ol>'
                    '<p>What would happen if step 5 came first? Or if step 3 was left out?</p>')},
                'video': {'id': 'FHsuEh1kJ18', 'title': 'Unplugged - Real-Life Algorithms: Planting a Seed',
                          'channel': 'CodeAI', 'minutes': 4},
                'worksheet': {'instructions': 'Answer the questions and write algorithms.',
                              'exercises': [
                                  'What is an algorithm? Write it in your own words.',
                                  'Put in order: Pour milk ( ) Get a bowl ( ) Eat ( ) Add cereal ( )',
                                  'Write an algorithm of 5 steps for washing your hands.',
                                  'Make this step precise: "Go to the place."',
                                  'Why does the order of steps matter?',
                              ]},
                'quiz': [
                    ('mcq', 'An algorithm must be ...', ['long and funny', 'clear and in order', 'secret'], 1),
                    ('tf', 'Algorithms are only used by computers, never by people.', False),
                    ('mcq', 'Which step is most precise?',
                     ['Put 1 seed in the hole.', 'Do the seed thing.', 'Put some stuff in.'], 0),
                    ('mcq', 'Following a recipe is an example of ...', ['a pattern', 'a robot', 'an algorithm'], 2),
                ],
                'homework': {'title': 'Recipe algorithm',
                             'instructions': 'Write an algorithm for a simple snack you can make with a grown-up.',
                             'tasks': ['Write 5 to 8 precise steps.',
                                       'Make the snack with a grown-up, following your steps exactly.',
                                       'Write one step you had to change.'],
                             'marks': 12},
            },
            {
                'title': 'My robotic friends: coding with symbols',
                'minutes': 35,
                'objectives': [
                    'I can write a program using symbols.',
                    'I can follow a program step by step.',
                    'I can use a repeat to make my program shorter.',
                ],
                'notes': (
                    '<p>Programmers use a small set of <strong>symbols</strong> (commands). Today we use:</p>'
                    '<ul><li><strong>F</strong> = step forward</li>'
                    '<li><strong>L</strong> = turn left (stay on the same spot)</li>'
                    '<li><strong>R</strong> = turn right (stay on the same spot)</li>'
                    '<li><strong>P</strong> = pick up</li></ul>'
                    '<p>A <strong>program</strong> is a list of commands. F F R F P means: forward, forward, '
                    'turn right, forward, pick up.</p>'
                    '<p>A <strong>repeat</strong> saves writing: <em>repeat 3 [F]</em> is the same as F F F.</p>'
                ),
                'key_terms': [('program', 'an algorithm written in code'),
                              ('command', 'one instruction in a program'),
                              ('repeat (loop)', 'do the same command again a number of times')],
                'example': {'title': 'Class activity: My Robotic Friends', 'html': (
                    '<p>In pairs, one learner is the programmer and one is the robot.</p>'
                    '<ol><li>Place a cup 3 steps in front of the robot, then 2 steps to its right.</li>'
                    '<li>Programmer writes: F F F R F F P.</li>'
                    '<li>With a repeat: repeat 3 [F], R, repeat 2 [F], P.</li>'
                    '<li>The robot follows the program exactly. Swap roles.</li></ol>')},
                'video': {'id': 'xaW3PAzHxCU', 'title': 'My Robotic Friends - unplugged activity',
                          'channel': 'CodeAI', 'minutes': 5},
                'worksheet': {'instructions': 'Use F, L, R and P. Draw a grid to help you.',
                              'exercises': [
                                  'Read the program F F L F. Describe what the robot does.',
                                  'Write a program: forward 4 steps, then pick up.',
                                  'Rewrite F F F F F using a repeat.',
                                  'Write a program to go forward 2, turn right, forward 3 and pick up.',
                                  'Write a program for a robot to walk in a square (hint: repeat 4).',
                              ]},
                'quiz': [
                    ('mcq', 'In our code, what does F mean?', ['finish', 'fall', 'step forward'], 2),
                    ('mcq', 'Which is the same as F F F?', ['repeat 3 [F]', 'repeat 2 [F]', 'F R F'], 0),
                    ('tf', 'A program is a list of commands.', True),
                    ('mcq', 'What does "R" do in our code?', ['run', 'turn right', 'repeat'], 1),
                ],
                'homework': {'title': 'Program a family robot',
                             'instructions': 'Your grown-up is the robot!',
                             'tasks': ['Hide a small object in a room.',
                                       'Write a program using F, L, R and P to guide your grown-up to it.',
                                       'Use at least one repeat in your program.'],
                             'marks': 12},
            },
            {
                'title': 'Debugging: finding and fixing mistakes',
                'minutes': 35,
                'objectives': [
                    'I can explain what a bug is.',
                    'I can find the step where a program goes wrong.',
                    'I can fix a program and test it again.',
                ],
                'notes': (
                    '<p>A <strong>bug</strong> is a mistake in a program. '
                    '<strong>Debugging</strong> means finding and fixing the bug.</p>'
                    '<ol><li><strong>Run</strong> the program and watch what happens.</li>'
                    '<li>Go through it step by step. Find the step where it goes wrong.</li>'
                    '<li><strong>Fix</strong> that step.</li>'
                    '<li><strong>Test</strong> again.</li></ol>'
                    '<p>Everyone makes bugs, even expert programmers. Good coders are patient and keep trying.</p>'
                ),
                'key_terms': [('bug', 'a mistake in a program'),
                              ('debug', 'find and fix the mistakes'),
                              ('test', 'run the program to check that it works')],
                'example': {'title': 'Worked example: debug the robot', 'html': (
                    '<p>The robot must go forward 3 steps, turn right and pick up a ball 1 step ahead.</p>'
                    '<p>Program: <strong>F F R F P</strong>. The robot misses the ball!</p>'
                    '<ol><li>Step through: F, F ... the robot turned after only 2 steps.</li>'
                    '<li>Bug: one F is missing.</li>'
                    '<li>Fixed: <strong>F F F R F P</strong>. Test again: it works!</li></ol>')},
                'video': {'id': 'M6jokEIj4qQ',
                          'title': 'Free Coding tutorial for kids | What is Debugging ? | Debugging  for Kids | Debug code to fix bugs',
                          'channel': 'JrDinoCoders', 'minutes': 5},
                'worksheet': {'instructions': 'Find the bug in each program and fix it.',
                              'exercises': [
                                  'Goal: forward 4, pick up. Program: F F F P. Fix it.',
                                  'Goal: forward 2, turn left, forward 1. Program: F F R F. Fix it.',
                                  'Goal: brush teeth. Steps: brush, rinse, put on toothpaste. Fix the order.',
                                  'Goal: forward 3. Program: repeat 4 [F]. Fix it.',
                                  'What are the 4 steps of debugging?',
                              ]},
                'quiz': [
                    ('mcq', 'A bug in a program is ...', ['an insect', 'a mistake', 'a robot'], 1),
                    ('tf', 'After fixing a bug, we should test the program again.', True),
                    ('mcq', 'Goal: forward 3. Program: F F. What is the bug?',
                     ['one F is missing', 'too many Fs', 'there is no bug'], 0),
                    ('tf', 'Expert programmers never make bugs.', False),
                ],
                'homework': {'title': 'Bug hunt',
                             'instructions': 'Test an algorithm with a grown-up and debug it.',
                             'tasks': ['Write an algorithm for getting from your bed to the kitchen.',
                                       'Ask a grown-up to follow it exactly. Note where it goes wrong.',
                                       'Fix the bug and test it again.'],
                             'marks': 12},
            },
        ],
    },
}
