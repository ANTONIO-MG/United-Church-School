"""Senior Phase (A): Term 1, Week 1 demo lessons for Grades 7, 8 and 9.

Offerings (12): grades 7, 8, 9 x
    ENG-HL   English Home Language
    ZUL-FAL  isiZulu First Additional Language
    MATH     Mathematics
    NAT-SCI  Natural Sciences

CAPS sources used:
    * CAPS Senior Phase Mathematics (Gr 7-9) and the DBE Annual Teaching Plans for Term 1:
      Gr 7 Whole numbers (properties, multiples and factors, HCF/LCM); Gr 8 Whole numbers
      (properties, prime factorisation, HCF/LCM, ratio and rate); Gr 9 Whole numbers and the
      number system (natural, whole, integers, rational, irrational; ratio, rate, proportion).
    * CAPS Senior Phase Natural Sciences (Gr 7-9), Strand Life and Living, Term 1:
      Gr 7 "The biosphere"; Gr 8 "Photosynthesis and respiration" / "Interactions and
      interdependence within the environment" (Ecosystems); Gr 9 "Cells as the basic units of life".
    * CAPS Senior Phase English Home Language, Term 1 Weeks 1-2 cycle: listening and speaking,
      reading and viewing (short story / poetry), writing and presenting (narrative /
      descriptive essay), language structures and conventions (parts of speech, sentences).
    * CAPS Senior Phase isiZulu First Additional Language, Term 1: listening and speaking
      (izibingelelo, ukuzethula nokwethula abanye, ingxoxo), reading (ukufunda nokuqonda
      umbhalo omfushane), language structures (izigaba zamabizo, izabizwana).
All reading texts (stories, poem, isiZulu passages) are original and written for these lessons.
"""

LESSONS = {
    # ======================================================================
    # GRADE 7 MATHEMATICS
    # ======================================================================
    (7, 'MATH'): {
        'topic': 'Whole numbers: properties, multiples, factors, HCF and LCM',
        'caps': 'Numbers, Operations and Relationships - Whole numbers: properties of whole numbers '
                '(commutative, associative, distributive; 0 and 1), multiples and factors, prime and '
                'composite numbers, HCF and LCM of numbers to at least 3 digits (CAPS Gr 7, Term 1)',
        'summary': 'Learners revise the properties of whole numbers and use them for mental calculation, '
                   'then work with factors, multiples and prime numbers, and finally find the HCF and LCM '
                   'to solve everyday problems.',
        'days': [
            {
                'title': 'Properties of whole numbers',
                'minutes': 50,
                'objectives': [
                    'I can name and recognise the commutative, associative and distributive properties.',
                    'I can explain the role of 0 and 1 in addition and multiplication.',
                    'I can use the properties to calculate quickly in my head.',
                ],
                'notes': (
                    '<p><strong>Whole numbers</strong> are the numbers 0, 1, 2, 3, 4, ... They follow '
                    'rules called <strong>properties</strong>. Knowing these rules helps us calculate '
                    'faster and check our work.</p>'
                    '<ul>'
                    '<li><strong>Commutative property:</strong> the order does not matter for addition and '
                    'multiplication. 8 + 5 = 5 + 8 and 6 × 4 = 4 × 6. It does <em>not</em> work for '
                    'subtraction or division: 10 - 4 is not equal to 4 - 10.</li>'
                    '<li><strong>Associative property:</strong> the grouping does not matter for addition and '
                    'multiplication. (7 + 3) + 9 = 7 + (3 + 9) and (2 × 5) × 6 = 2 × (5 × 6).</li>'
                    '<li><strong>Distributive property:</strong> multiplication can be spread over addition '
                    'or subtraction. 6 × (10 + 3) = 6 × 10 + 6 × 3 = 60 + 18 = 78.</li>'
                    '<li><strong>Identity (0 and 1):</strong> adding 0 leaves a number unchanged '
                    '(45 + 0 = 45); multiplying by 1 leaves it unchanged (45 × 1 = 45).</li>'
                    '<li><strong>Zero in multiplication:</strong> any number multiplied by 0 is 0. '
                    'Division by 0 is not possible.</li>'
                    '</ul>'
                    '<p>We use these properties to make "friendly numbers". For example, to work out '
                    '25 × 17 × 4 we can swap and regroup: (25 × 4) × 17 = 100 × 17 = 1 700.</p>'
                ),
                'key_terms': [
                    ('commutative', 'the order of the numbers can change without changing the answer'),
                    ('associative', 'the grouping of the numbers can change without changing the answer'),
                    ('distributive', 'a(b + c) = ab + ac: multiply each part inside the brackets'),
                    ('additive identity', '0, because n + 0 = n'),
                    ('multiplicative identity', '1, because n × 1 = n'),
                ],
                'example': {
                    'title': 'Worked example: calculating smartly',
                    'html': (
                        '<p><strong>a)</strong> 8 × 53 = 8 × (50 + 3) = 400 + 24 = <strong>424</strong> '
                        '(distributive property)</p>'
                        '<p><strong>b)</strong> 36 + 87 + 64 = (36 + 64) + 87 = 100 + 87 = <strong>187</strong> '
                        '(commutative and associative properties)</p>'
                        '<p><strong>c)</strong> 9 × 99 = 9 × (100 - 1) = 900 - 9 = <strong>891</strong> '
                        '(distributive property over subtraction)</p>'
                    ),
                },
                'video': {'id': 'mgw2JfwtT5E',
                          'title': 'Properties: Commutative, Associative, Distributive, and Identity',
                          'channel': 'Super Easy Math', 'minutes': 6},
                'worksheet': {
                    'instructions': 'Name the property used, or use a property to calculate without a calculator. Show your steps.',
                    'exercises': [
                        '1. Name the property: 14 + 29 = 29 + 14',
                        '2. Name the property: (3 × 7) × 5 = 3 × (7 × 5)',
                        '3. Name the property: 4 × (20 + 6) = 4 × 20 + 4 × 6',
                        '4. Calculate smartly: 50 × 39 × 2',
                        '5. Calculate using the distributive property: 7 × 48',
                        '6. Calculate smartly: 125 + 389 + 75',
                        '7. Is 20 ÷ 4 = 4 ÷ 20? What does this tell you about division?',
                        '8. Fill in the missing number: 6 × (9 + __) = 54 + 12',
                    ],
                },
                'quiz': [
                    ('mcq', 'Which property is shown by 7 + 5 = 5 + 7?',
                     ['Associative', 'Commutative', 'Distributive', 'Identity'], 1),
                    ('mcq', 'What is 6 × (10 + 3)?', ['63', '33', '78', '19'], 2),
                    ('tf', 'Subtraction is commutative, so 12 - 5 = 5 - 12.', False),
                    ('mcq', 'Which number is the multiplicative identity?', ['1', '0', '10', '-1'], 0),
                    ('tf', 'Any whole number multiplied by 0 gives 0.', True),
                ],
                'homework': {
                    'title': 'Properties in action',
                    'instructions': 'Use the properties of whole numbers to calculate. Write down the property you used each time.',
                    'tasks': [
                        'Calculate 4 × 67 × 25 in the quickest way.',
                        'Calculate 12 × 105 using the distributive property.',
                        'Write your own example of the associative property for addition.',
                    ],
                    'marks': 10,
                },
            },
            {
                'title': 'Factors, multiples and prime numbers',
                'minutes': 50,
                'objectives': [
                    'I can list the factors of a number and the first few multiples of a number.',
                    'I can tell the difference between prime and composite numbers.',
                    'I can use divisibility rules to test for factors.',
                ],
                'notes': (
                    '<p>A <strong>factor</strong> of a number divides into it exactly, with no remainder. '
                    'The factors of 24 are 1, 2, 3, 4, 6, 8, 12 and 24. Factors come in pairs: '
                    '1 × 24, 2 × 12, 3 × 8, 4 × 6.</p>'
                    '<p>A <strong>multiple</strong> of a number is the answer when you multiply it by a '
                    'whole number. The multiples of 6 are 6, 12, 18, 24, 30, ... A number has a limited '
                    'number of factors but an endless list of multiples.</p>'
                    '<p>A <strong>prime number</strong> has exactly two factors: 1 and itself '
                    '(2, 3, 5, 7, 11, 13, 17, 19, ...). A <strong>composite number</strong> has more than '
                    'two factors (4, 6, 8, 9, 10, ...). The number 1 is neither prime nor composite, and '
                    '2 is the only even prime number.</p>'
                    '<p><strong>Divisibility rules</strong> help us test for factors quickly:</p>'
                    '<ul>'
                    '<li>by 2: the last digit is even;</li>'
                    '<li>by 3: the sum of the digits is divisible by 3;</li>'
                    '<li>by 5: the last digit is 0 or 5;</li>'
                    '<li>by 9: the sum of the digits is divisible by 9;</li>'
                    '<li>by 10: the last digit is 0.</li>'
                    '</ul>'
                ),
                'key_terms': [
                    ('factor', 'a number that divides exactly into another number'),
                    ('multiple', 'the product of a number and any whole number'),
                    ('prime number', 'a number with exactly two factors: 1 and itself'),
                    ('composite number', 'a number with more than two factors'),
                ],
                'example': {
                    'title': 'Worked example: factor pairs and divisibility',
                    'html': (
                        '<p><strong>Find all the factors of 36.</strong></p>'
                        '<p>Factor pairs: 1 × 36, 2 × 18, 3 × 12, 4 × 9, 6 × 6.</p>'
                        '<p>Factors: 1, 2, 3, 4, 6, 9, 12, 18, 36 (nine factors, so 36 is composite).</p>'
                        '<p><strong>Is 4 581 divisible by 3?</strong> 4 + 5 + 8 + 1 = 18, and 18 is '
                        'divisible by 3, so <strong>yes</strong>. (18 is also divisible by 9, so 4 581 is '
                        'divisible by 9 as well.)</p>'
                    ),
                },
                'video': {'id': 'u2xg0CbWomk',
                          'title': 'Factors, Prime Numbers & Prime Factors Grade 7 8 and 9 maths',
                          'channel': 'Miss Martins Maths and Science', 'minutes': 10},
                'worksheet': {
                    'instructions': 'Answer each question. Show your factor pairs or working.',
                    'exercises': [
                        '1. List all the factors of 48.',
                        '2. Write down the first six multiples of 7.',
                        '3. List all the prime numbers between 20 and 50.',
                        '4. Is 51 prime or composite? Explain.',
                        '5. Use the divisibility rule to test whether 7 236 is divisible by 3.',
                        '6. Which of these numbers are multiples of 5: 35, 52, 80, 105, 123?',
                        '7. Explain why 1 is not a prime number.',
                    ],
                },
                'quiz': [
                    ('mcq', 'Which of these is a prime number?', ['21', '27', '29', '33'], 2),
                    ('tf', 'The number 2 is the only even prime number.', True),
                    ('mcq', 'How many factors does 24 have?', ['6', '8', '4', '10'], 1),
                    ('tf', '42 is a multiple of 8.', False),
                    ('mcq', 'A number is divisible by 9 if ...',
                     ['it ends in 9', 'it is odd', 'the sum of its digits is divisible by 9',
                      'it is greater than 9'], 2),
                ],
                'homework': {
                    'title': 'Prime number hunt',
                    'instructions': 'Use the Sieve of Eratosthenes on a 1 to 100 grid to find the primes.',
                    'tasks': [
                        'Draw a 10 by 10 grid with the numbers 1 to 100.',
                        'Cross out 1, then cross out all multiples of 2, 3, 5 and 7 (but not 2, 3, 5 and 7 themselves).',
                        'Circle the numbers that are left. How many prime numbers are there below 100?',
                    ],
                    'marks': 10,
                },
            },
            {
                'title': 'HCF and LCM',
                'minutes': 55,
                'objectives': [
                    'I can find the highest common factor (HCF) of two or three numbers.',
                    'I can find the lowest common multiple (LCM) of two or three numbers.',
                    'I can decide whether a word problem needs the HCF or the LCM.',
                ],
                'notes': (
                    '<p>The <strong>highest common factor (HCF)</strong> is the biggest number that is a '
                    'factor of all the given numbers.</p>'
                    '<p>Example: factors of 12 are 1, 2, 3, 4, 6, 12; factors of 18 are 1, 2, 3, 6, 9, 18. '
                    'The common factors are 1, 2, 3 and 6, so the <strong>HCF is 6</strong>.</p>'
                    '<p>The <strong>lowest common multiple (LCM)</strong> is the smallest number (other than 0) '
                    'that is a multiple of all the given numbers.</p>'
                    '<p>Example: multiples of 4 are 4, 8, 12, 16, 20, 24 ...; multiples of 6 are 6, 12, 18, '
                    '24 ... The common multiples are 12, 24, ..., so the <strong>LCM is 12</strong>.</p>'
                    '<p><strong>Which one do I need?</strong></p>'
                    '<ul>'
                    '<li>Use the <strong>HCF</strong> when you are <em>sharing or cutting</em> things into the '
                    'largest equal groups or pieces.</li>'
                    '<li>Use the <strong>LCM</strong> when you want to know when things will '
                    '<em>happen together again</em> or find the smallest amount that fits both.</li>'
                    '</ul>'
                    '<p>A useful check for two numbers: HCF × LCM = the product of the numbers. '
                    'For 4 and 6: 2 × 12 = 24 = 4 × 6.</p>'
                ),
                'key_terms': [
                    ('HCF', 'highest common factor: the largest factor shared by the numbers'),
                    ('LCM', 'lowest common multiple: the smallest multiple shared by the numbers'),
                    ('common factor', 'a number that is a factor of two or more numbers'),
                ],
                'example': {
                    'title': 'Worked example: HCF or LCM?',
                    'html': (
                        '<p><strong>Problem 1:</strong> Two taxis leave the rank at 07:00. One returns every '
                        '12 minutes and the other every 15 minutes. When will they be at the rank together again?</p>'
                        '<p>Multiples of 12: 12, 24, 36, 48, <strong>60</strong>. Multiples of 15: 15, 30, 45, '
                        '<strong>60</strong>. LCM = 60 minutes, so they meet again at <strong>08:00</strong>.</p>'
                        '<p><strong>Problem 2:</strong> A 24 m rope and a 36 m rope must be cut into pieces '
                        'that are all the same length, as long as possible, with nothing left over.</p>'
                        '<p>Common factors of 24 and 36: 1, 2, 3, 4, 6, 12. HCF = <strong>12 m</strong>, so we get '
                        '2 + 3 = 5 pieces.</p>'
                    ),
                },
                'video': {'id': 'N_S_wrN8ue8',
                          'title': 'Factors vs. Multiples Explained | Common Factors, GCF, and LCM',
                          'channel': 'Math with Mr. J', 'minutes': 8},
                'worksheet': {
                    'instructions': 'Find the HCF or LCM by listing factors or multiples. For word problems, say whether you used the HCF or the LCM.',
                    'exercises': [
                        '1. Find the HCF of 16 and 40.',
                        '2. Find the HCF of 18, 27 and 45.',
                        '3. Find the LCM of 6 and 8.',
                        '4. Find the LCM of 3, 4 and 10.',
                        '5. A teacher has 30 pencils and 42 erasers to pack into identical packs with nothing left over. What is the largest number of packs she can make?',
                        '6. One light flashes every 8 seconds and another every 10 seconds. They flash together now. After how many seconds will they flash together again?',
                        '7. Check that HCF × LCM = 16 × 40 for the numbers in question 1.',
                    ],
                },
                'quiz': [
                    ('mcq', 'What is the HCF of 12 and 18?', ['3', '36', '2', '6'], 3),
                    ('mcq', 'What is the LCM of 4 and 6?', ['12', '24', '2', '10'], 0),
                    ('tf', 'The LCM of two numbers can be smaller than both numbers.', False),
                    ('mcq', 'Buses leave every 10 and every 25 minutes. To find when they leave together again you need the ...',
                     ['HCF', 'sum', 'LCM', 'difference'], 2),
                ],
                'homework': {
                    'title': 'HCF and LCM in real life',
                    'instructions': 'Solve the problems and show how you found the HCF or LCM.',
                    'tasks': [
                        'Find the HCF and the LCM of 20 and 30.',
                        'Hot dog rolls come in packs of 6 and sausages in packs of 8. What is the smallest number of each you can buy to have the same number of rolls and sausages?',
                        'Write and solve your own word problem that needs the HCF.',
                    ],
                    'marks': 12,
                },
            },
        ],
    },

    # ======================================================================
    # GRADE 8 MATHEMATICS
    # ======================================================================
    (8, 'MATH'): {
        'topic': 'Whole numbers: properties, prime factorisation, HCF, LCM, ratio and rate',
        'caps': 'Numbers, Operations and Relationships - Whole numbers: revise properties of natural and '
                'whole numbers; multiples and factors, prime factorisation, LCM and HCF of numbers; '
                'solve problems involving ratio and rate (CAPS Gr 8, Term 1)',
        'summary': 'Learners revise the number sets and properties of whole numbers, write numbers as '
                   'products of prime factors, use prime factors to find HCF and LCM, and solve ratio and '
                   'rate problems.',
        'days': [
            {
                'title': 'Natural and whole numbers; prime factorisation',
                'minutes': 50,
                'objectives': [
                    'I can describe the sets of natural numbers (N) and whole numbers (N0).',
                    'I can use the properties of whole numbers in calculations.',
                    'I can write a number as a product of its prime factors using a factor tree or ladder.',
                ],
                'notes': (
                    '<p><strong>Natural numbers</strong> are the counting numbers: N = {1; 2; 3; 4; ...}. '
                    '<strong>Whole numbers</strong> are the natural numbers together with 0: '
                    'N0 = {0; 1; 2; 3; ...}.</p>'
                    '<p>Remember the properties: addition and multiplication are <strong>commutative</strong> '
                    'and <strong>associative</strong>, multiplication is <strong>distributive</strong> over '
                    'addition and subtraction, 0 is the additive identity and 1 is the multiplicative identity.</p>'
                    '<p>Every composite number can be written as a <strong>product of prime factors</strong> '
                    'in exactly one way (ignoring order). This is called <strong>prime factorisation</strong>.</p>'
                    '<p><strong>Ladder (repeated division) method:</strong> keep dividing by the smallest '
                    'prime that divides exactly, until you reach 1.</p>'
                    '<ul>'
                    '<li>360 ÷ 2 = 180; 180 ÷ 2 = 90; 90 ÷ 2 = 45</li>'
                    '<li>45 ÷ 3 = 15; 15 ÷ 3 = 5; 5 ÷ 5 = 1</li>'
                    '</ul>'
                    '<p>So 360 = 2 × 2 × 2 × 3 × 3 × 5 = <strong>2³ × 3² × 5</strong>. Writing repeated '
                    'factors with exponents keeps the answer neat.</p>'
                ),
                'key_terms': [
                    ('natural numbers (N)', '{1; 2; 3; ...}'),
                    ('whole numbers (N0)', '{0; 1; 2; 3; ...}'),
                    ('prime factor', 'a factor of a number that is itself a prime number'),
                    ('prime factorisation', 'writing a number as a product of prime numbers only'),
                ],
                'example': {
                    'title': 'Worked example: factor tree',
                    'html': (
                        '<p><strong>Write 84 as a product of prime factors.</strong></p>'
                        '<p>84 = 2 × 42<br>42 = 2 × 21<br>21 = 3 × 7</p>'
                        '<p>So 84 = 2 × 2 × 3 × 7 = <strong>2² × 3 × 7</strong>.</p>'
                        '<p>Check: 4 × 3 × 7 = 12 × 7 = 84.</p>'
                        '<p><strong>Mental maths with properties:</strong> 5 × 46 × 20 = (5 × 20) × 46 = '
                        '100 × 46 = 4 600.</p>'
                    ),
                },
                'video': {'id': 'eJ9l_YibuRI', 'title': 'Gr8 Maths | Term 1 | Lesson 1 | Whole numbers',
                          'channel': 'Thuma Mina Teaching', 'minutes': 15},
                'worksheet': {
                    'instructions': 'Answer all questions. Write prime factorisations using exponents where possible.',
                    'exercises': [
                        '1. Is 0 a natural number, a whole number, or both? Explain.',
                        '2. Use the distributive property to calculate 15 × 98.',
                        '3. Write 72 as a product of prime factors.',
                        '4. Write 150 as a product of prime factors.',
                        '5. Write 504 as a product of prime factors.',
                        '6. Which number has the prime factorisation 2² × 3² × 5?',
                        '7. Explain why 91 is not a prime number.',
                    ],
                },
                'quiz': [
                    ('tf', '0 is a whole number but not a natural number.', True),
                    ('mcq', 'What is the prime factorisation of 60?',
                     ['2 × 30', '2² × 3 × 5', '2 × 3 × 10', '4 × 15'], 1),
                    ('mcq', 'Which number equals 2³ × 3?', ['18', '12', '24', '36'], 2),
                    ('tf', 'The prime factorisation of 45 is 3² × 5.', True),
                ],
                'homework': {
                    'title': 'Prime factor practice',
                    'instructions': 'Use a factor tree or the ladder method. Show every step.',
                    'tasks': [
                        'Write 96 as a product of prime factors.',
                        'Write 1 000 as a product of prime factors.',
                        'Which number between 50 and 60 has the most prime factors (counting repeats)? Show why.',
                    ],
                    'marks': 10,
                },
            },
            {
                'title': 'HCF and LCM using prime factors',
                'minutes': 55,
                'objectives': [
                    'I can find the HCF of two or three numbers from their prime factorisations.',
                    'I can find the LCM of two or three numbers from their prime factorisations.',
                    'I can solve word problems involving HCF and LCM.',
                ],
                'notes': (
                    '<p>Listing factors and multiples works for small numbers, but for bigger numbers it is '
                    'quicker to use <strong>prime factorisation</strong>.</p>'
                    '<p><strong>Steps for the HCF:</strong></p>'
                    '<ol>'
                    '<li>Write each number as a product of prime factors.</li>'
                    '<li>Take only the primes that appear in <em>every</em> number.</li>'
                    '<li>Use the <em>lowest</em> power of each of those primes and multiply.</li>'
                    '</ol>'
                    '<p><strong>Steps for the LCM:</strong></p>'
                    '<ol>'
                    '<li>Write each number as a product of prime factors.</li>'
                    '<li>Take <em>every</em> prime that appears in any of the numbers.</li>'
                    '<li>Use the <em>highest</em> power of each prime and multiply.</li>'
                    '</ol>'
                    '<p>Example: 84 = 2² × 3 × 7 and 120 = 2³ × 3 × 5.</p>'
                    '<ul>'
                    '<li>HCF = 2² × 3 = <strong>12</strong></li>'
                    '<li>LCM = 2³ × 3 × 5 × 7 = <strong>840</strong></li>'
                    '</ul>'
                    '<p>Check for two numbers: HCF × LCM = 12 × 840 = 10 080 = 84 × 120.</p>'
                ),
                'key_terms': [
                    ('HCF', 'product of the common primes, each to its lowest power'),
                    ('LCM', 'product of all the primes, each to its highest power'),
                    ('exponent', 'the small number showing how many times a factor is repeated'),
                ],
                'example': {
                    'title': 'Worked example: three numbers',
                    'html': (
                        '<p><strong>Find the HCF and LCM of 18, 24 and 30.</strong></p>'
                        '<p>18 = 2 × 3²<br>24 = 2³ × 3<br>30 = 2 × 3 × 5</p>'
                        '<p>Common primes: 2 and 3. Lowest powers: 2¹ and 3¹. '
                        '<strong>HCF = 2 × 3 = 6</strong>.</p>'
                        '<p>All primes with highest powers: 2³, 3², 5. '
                        '<strong>LCM = 8 × 9 × 5 = 360</strong>.</p>'
                        '<p><em>Application:</em> Three bells ring every 18, 24 and 30 minutes. If they ring '
                        'together at noon, they next ring together after 360 minutes = 6 hours, at 18:00.</p>'
                    ),
                },
                'video': {'id': 'JVxIvwsMNDo', 'title': 'Finding the HCF and the LCM',
                          'channel': 'Maths Genie', 'minutes': 8},
                'worksheet': {
                    'instructions': 'Use prime factorisation to find the HCF and/or LCM. Show the prime factors of each number.',
                    'exercises': [
                        '1. Find the HCF and LCM of 36 and 48.',
                        '2. Find the HCF and LCM of 90 and 150.',
                        '3. Find the HCF of 42, 70 and 98.',
                        '4. Find the LCM of 12, 15 and 20.',
                        '5. Tiles measure 24 cm by 36 cm. What is the side of the smallest square that can be made from whole tiles?',
                        '6. 60 boys and 84 girls are split into teams. Each team has the same number of boys and the same number of girls. What is the largest number of teams?',
                    ],
                },
                'quiz': [
                    ('mcq', 'If a = 2² × 3 × 5 and b = 2 × 3², what is the HCF of a and b?',
                     ['6', '18', '180', '30'], 0),
                    ('mcq', 'Using the same a and b, what is the LCM?', ['90', '60', '180', '360'], 2),
                    ('tf', 'To find the LCM you use the highest power of every prime factor.', True),
                    ('mcq', 'What is the HCF of 84 and 120?', ['6', '24', '4', '12'], 3),
                ],
                'homework': {
                    'title': 'HCF and LCM with prime factors',
                    'instructions': 'Show the prime factorisation of every number before you find the HCF or LCM.',
                    'tasks': [
                        'Find the HCF and LCM of 56 and 84.',
                        'Find the LCM of 8, 12 and 18.',
                        'Two runners lap a track in 72 seconds and 80 seconds. They start together. After how many seconds will they pass the start line together again?',
                    ],
                    'marks': 12,
                },
            },
            {
                'title': 'Ratio and rate',
                'minutes': 55,
                'objectives': [
                    'I can simplify a ratio and share an amount in a given ratio.',
                    'I can calculate a rate and give it with the correct units.',
                    'I can use unit rates to compare prices (best buy).',
                ],
                'notes': (
                    '<p>A <strong>ratio</strong> compares two or more quantities measured in the <em>same</em> '
                    'unit. It has no units. 12 boys to 16 girls is 12 : 16, which simplifies to '
                    '<strong>3 : 4</strong> (divide both by the HCF, 4).</p>'
                    '<p><strong>Sharing in a ratio:</strong> add the parts to find the total number of parts, '
                    'find the value of one part, then multiply.</p>'
                    '<p>Share R360 in the ratio 4 : 5. Total parts = 9. One part = R360 ÷ 9 = R40. '
                    'Shares: 4 × R40 = <strong>R160</strong> and 5 × R40 = <strong>R200</strong>. '
                    'Check: R160 + R200 = R360.</p>'
                    '<p>A <strong>rate</strong> compares two quantities measured in <em>different</em> units, '
                    'so it always has units, for example km/h, R/kg or words per minute.</p>'
                    '<ul>'
                    '<li>A car travels 240 km in 3 hours: speed = 240 ÷ 3 = <strong>80 km/h</strong>.</li>'
                    '<li>A <strong>unit rate</strong> gives the amount for one unit, e.g. R19 per kg. Unit '
                    'rates let us compare prices fairly.</li>'
                    '</ul>'
                ),
                'key_terms': [
                    ('ratio', 'a comparison of quantities in the same unit, written a : b'),
                    ('simplest form', 'a ratio where the numbers have no common factor except 1'),
                    ('rate', 'a comparison of quantities in different units, e.g. km/h'),
                    ('unit rate', 'the rate for one unit, e.g. price per kilogram'),
                ],
                'example': {
                    'title': 'Worked example: best buy',
                    'html': (
                        '<p>Mealie meal is sold as <strong>2 kg for R38</strong> or <strong>5 kg for R90</strong>. '
                        'Which is the better buy?</p>'
                        '<p>2 kg: R38 ÷ 2 = <strong>R19,00 per kg</strong><br>'
                        '5 kg: R90 ÷ 5 = <strong>R18,00 per kg</strong></p>'
                        '<p>The 5 kg bag is the better buy because each kilogram costs less.</p>'
                        '<p><strong>Ratio check:</strong> simplify 45 : 60. HCF = 15, so 45 : 60 = 3 : 4.</p>'
                    ),
                },
                'video': {'id': 'iqT_PBzl-XU', 'title': 'Ratios Grade 8', 'channel': 'Kevinmathscience',
                          'minutes': 10},
                'worksheet': {
                    'instructions': 'Simplify ratios fully, show your working for sharing, and always give units for rates.',
                    'exercises': [
                        '1. Simplify 24 : 36.',
                        '2. Simplify 1,5 m : 75 cm (change to the same unit first).',
                        '3. Share R450 between Thabo and Lerato in the ratio 2 : 3.',
                        '4. Share 84 sweets in the ratio 1 : 2 : 4.',
                        '5. A tap fills a 120 litre drum in 8 minutes. Calculate the rate in litres per minute.',
                        '6. Which is cheaper per litre: 2 litres of milk for R34 or 5 litres for R80?',
                        '7. A cyclist rides at 18 km/h. How far will she ride in 2,5 hours?',
                    ],
                },
                'quiz': [
                    ('mcq', 'What is 15 : 25 in simplest form?', ['5 : 3', '3 : 5', '1 : 5', '15 : 25'], 1),
                    ('mcq', 'R120 is shared in the ratio 1 : 3. What is the larger share?',
                     ['R40', 'R30', 'R90', 'R80'], 2),
                    ('tf', 'A rate compares quantities with different units, such as km and hours.', True),
                    ('mcq', 'A car travels 150 km in 2 hours. What is its average speed?',
                     ['75 km/h', '300 km/h', '152 km/h', '50 km/h'], 0),
                ],
                'homework': {
                    'title': 'Ratio and rate at home',
                    'instructions': 'Use real or realistic examples from home. Show your calculations.',
                    'tasks': [
                        'Find a recipe at home (or make one up) and write the ratio of two ingredients. Then double the recipe.',
                        'Compare two pack sizes of the same product (from a shop slip or advert) and decide which is the better buy.',
                        'Share R240 in the ratio 3 : 5.',
                    ],
                    'marks': 12,
                },
            },
        ],
    },

    # ======================================================================
    # GRADE 9 MATHEMATICS
    # ======================================================================
    (9, 'MATH'): {
        'topic': 'Whole numbers and the number system; ratio, rate and proportion',
        'caps': 'Numbers, Operations and Relationships - Whole numbers: revise the real number system '
                '(natural, whole, integers, rational and irrational numbers); properties of numbers; '
                'solve problems involving ratio, rate and direct and indirect proportion (CAPS Gr 9, Term 1)',
        'summary': 'Learners classify numbers in the real number system, distinguish rational from '
                   'irrational numbers and use additive and multiplicative inverses, then solve ratio, '
                   'direct proportion and indirect proportion problems.',
        'days': [
            {
                'title': 'The real number system',
                'minutes': 50,
                'objectives': [
                    'I can describe natural numbers, whole numbers, integers, rational and irrational numbers.',
                    'I can classify a given number into every set it belongs to.',
                    'I can explain how the number sets fit inside one another.',
                ],
                'notes': (
                    '<p>Mathematicians group numbers into <strong>sets</strong>. Each set contains the one '
                    'before it.</p>'
                    '<ul>'
                    '<li><strong>Natural numbers</strong> N = {1; 2; 3; ...}</li>'
                    '<li><strong>Whole numbers</strong> N0 = {0; 1; 2; 3; ...}</li>'
                    '<li><strong>Integers</strong> Z = {...; -3; -2; -1; 0; 1; 2; 3; ...}</li>'
                    '<li><strong>Rational numbers</strong> Q: any number that can be written as a/b where a '
                    'and b are integers and b is not 0. This includes fractions, terminating decimals '
                    '(0,75 = 3/4) and recurring decimals (0,333... = 1/3).</li>'
                    '<li><strong>Irrational numbers</strong>: numbers that <em>cannot</em> be written as a '
                    'fraction of integers. Their decimals never end and never repeat, e.g. pi, '
                    'the square root of 2, the square root of 5.</li>'
                    '<li><strong>Real numbers</strong> R: all rational and irrational numbers together.</li>'
                    '</ul>'
                    '<p>So N is inside N0, which is inside Z, which is inside Q, and Q and the '
                    'irrationals together make R. A number such as 7 belongs to <em>all</em> of N, '
                    'N0, Z, Q and R.</p>'
                    '<p>Be careful: the square root of 9 is 3, which is natural, so not every square root is '
                    'irrational.</p>'
                ),
                'key_terms': [
                    ('integer', 'a positive or negative whole number, or zero'),
                    ('rational number', 'a number that can be written as a/b with a, b integers and b not 0'),
                    ('irrational number', 'a number that cannot be written as a fraction of integers'),
                    ('real numbers', 'the set of all rational and irrational numbers'),
                ],
                'example': {
                    'title': 'Worked example: classify the numbers',
                    'html': (
                        '<p><strong>-4:</strong> integer, rational, real (not natural, not whole).</p>'
                        '<p><strong>0:</strong> whole, integer, rational, real (not natural).</p>'
                        '<p><strong>2,25:</strong> rational (= 9/4), real.</p>'
                        '<p><strong>Square root of 16:</strong> = 4, so natural, whole, integer, rational, real.</p>'
                        '<p><strong>Square root of 7:</strong> irrational, real (7 is not a perfect square).</p>'
                        '<p><strong>pi:</strong> irrational, real. (22/7 is only an <em>approximation</em> of pi.)</p>'
                    ),
                },
                'video': {'id': 'vFK3sjL7-f0',
                          'title': 'Gr9 Maths | Term 1 | Lesson 1 | Whole Numbers: The Real Number System',
                          'channel': 'Thuma Mina Teaching', 'minutes': 15},
                'worksheet': {
                    'instructions': 'Classify each number by writing down ALL the sets it belongs to (N, N0, Z, Q, irrational, R).',
                    'exercises': [
                        '1. 12',
                        '2. -7',
                        '3. 0',
                        '4. 3/8',
                        '5. 0,121212... (recurring)',
                        '6. Square root of 49',
                        '7. Square root of 10',
                        '8. Give an example of a number that is an integer but not a whole number.',
                    ],
                },
                'quiz': [
                    ('mcq', 'Which of these is an irrational number?',
                     ['0,5', 'Square root of 25', 'Square root of 3', '-8'], 2),
                    ('tf', 'Every integer is also a rational number.', True),
                    ('mcq', 'To which smallest set does -5 belong?',
                     ['Natural numbers', 'Whole numbers', 'Integers', 'Irrational numbers'], 2),
                    ('tf', '0,333... (recurring) is irrational because it never ends.', False),
                    ('mcq', 'Which number is whole but not natural?', ['1', '0', '-1', '1/2'], 1),
                ],
                'homework': {
                    'title': 'Number system diagram',
                    'instructions': 'Draw a neat diagram (nested ovals or boxes) of the real number system.',
                    'tasks': [
                        'Draw and label the sets N, N0, Z, Q, irrational numbers and R.',
                        'Place these numbers in the correct part of your diagram: 5; -2; 0; 1/4; 0,6; pi; square root of 2; square root of 36.',
                        'Explain in one sentence why pi is not a rational number.',
                    ],
                    'marks': 10,
                },
            },
            {
                'title': 'Rational numbers, inverses and properties',
                'minutes': 50,
                'objectives': [
                    'I can convert a recurring decimal to a common fraction.',
                    'I can find the additive inverse and the multiplicative inverse (reciprocal) of a number.',
                    'I can apply the properties of real numbers in calculations.',
                ],
                'notes': (
                    '<p>Every <strong>terminating</strong> or <strong>recurring</strong> decimal is rational, '
                    'so it can be written as a fraction.</p>'
                    '<p><strong>Terminating:</strong> 0,35 = 35/100 = 7/20.</p>'
                    '<p><strong>Recurring:</strong> let x = 0,666... Then 10x = 6,666... Subtract: '
                    '10x - x = 6, so 9x = 6 and x = 6/9 = <strong>2/3</strong>.</p>'
                    '<p><strong>Inverses:</strong></p>'
                    '<ul>'
                    '<li>The <strong>additive inverse</strong> of a number gives 0 when added to it. '
                    'The additive inverse of 8 is -8, because 8 + (-8) = 0.</li>'
                    '<li>The <strong>multiplicative inverse</strong> (reciprocal) gives 1 when multiplied '
                    'by the number. The reciprocal of 5 is 1/5; the reciprocal of 2/3 is 3/2. '
                    '0 has no reciprocal.</li>'
                    '</ul>'
                    '<p>The commutative, associative and distributive properties you know from whole numbers '
                    'also hold for all real numbers. For example, -3 × (4 + 6) = -12 + (-18) = -30.</p>'
                ),
                'key_terms': [
                    ('terminating decimal', 'a decimal that ends, e.g. 0,125'),
                    ('recurring decimal', 'a decimal in which one or more digits repeat forever, e.g. 0,272727...'),
                    ('additive inverse', 'the number you add to get 0, e.g. -8 for 8'),
                    ('reciprocal', 'the multiplicative inverse: the number you multiply by to get 1'),
                ],
                'example': {
                    'title': 'Worked example: recurring decimal with two repeating digits',
                    'html': (
                        '<p><strong>Write 0,272727... as a fraction in simplest form.</strong></p>'
                        '<p>Let x = 0,2727...<br>'
                        'Two digits repeat, so multiply by 100: 100x = 27,2727...<br>'
                        'Subtract: 100x - x = 27, so 99x = 27<br>'
                        'x = 27/99 = <strong>3/11</strong> (divide by the HCF, 9).</p>'
                        '<p>Check on a calculator: 3 ÷ 11 = 0,272727...</p>'
                    ),
                },
                'video': {'id': 'Th9mT4TxvOI', 'title': 'An Intro to Rational and Irrational Numbers | Math with Mr. J',
                          'channel': 'Math with Mr. J', 'minutes': 7},
                'worksheet': {
                    'instructions': 'Show all steps. Give fractions in simplest form.',
                    'exercises': [
                        '1. Write 0,45 as a common fraction.',
                        '2. Write 0,777... (recurring) as a common fraction.',
                        '3. Write 0,151515... (recurring) as a common fraction.',
                        '4. Give the additive inverse of -12 and of 3/4.',
                        '5. Give the reciprocal of 7, of 2/5 and of -1/3.',
                        '6. Use the distributive property: -5 × (8 - 3).',
                        '7. Explain why 0 has no reciprocal.',
                    ],
                },
                'quiz': [
                    ('mcq', 'What is 0,444... (recurring) as a fraction?', ['4/10', '4/9', '1/4', '44/100'], 1),
                    ('mcq', 'What is the reciprocal of 3/7?', ['-3/7', '7/3', '3/7', '-7/3'], 1),
                    ('tf', 'The additive inverse of -9 is 9.', True),
                    ('mcq', 'Which number has no multiplicative inverse?', ['1', '-1', '0', '1/2'], 2),
                ],
                'homework': {
                    'title': 'Decimals and inverses',
                    'instructions': 'Complete the tasks in your exercise book.',
                    'tasks': [
                        'Write 0,8333... (only the 3 recurs) as a fraction. Hint: start with 10x and 100x.',
                        'Write down the additive inverse and the reciprocal of 4, -2/3 and 0,5.',
                        'Explain the difference between a recurring decimal and the decimal of an irrational number.',
                    ],
                    'marks': 10,
                },
            },
            {
                'title': 'Ratio, rate and direct and indirect proportion',
                'minutes': 55,
                'objectives': [
                    'I can share amounts in a ratio with three parts.',
                    'I can recognise and solve direct proportion problems.',
                    'I can recognise and solve indirect (inverse) proportion problems.',
                ],
                'notes': (
                    '<p><strong>Ratio</strong> compares quantities in the same unit; a <strong>rate</strong> '
                    'compares quantities in different units (km/h, R/kg).</p>'
                    '<p><strong>Direct proportion:</strong> when one quantity increases, the other increases '
                    'at the <em>same rate</em>. The ratio stays constant: y/x = k. Example: the more pens you '
                    'buy, the more you pay. If 5 pens cost R35, one pen costs R7 and 8 pens cost R56.</p>'
                    '<p><strong>Indirect (inverse) proportion:</strong> when one quantity increases, the other '
                    'decreases so that the <em>product</em> stays constant: x × y = k. Example: more workers '
                    'take fewer days to finish a job.</p>'
                    '<ul>'
                    '<li>Ask: "If I double one quantity, does the other double (direct) or halve (indirect)?"</li>'
                    '<li>Direct: use the unit amount (divide, then multiply).</li>'
                    '<li>Indirect: find the constant product (multiply, then divide).</li>'
                    '</ul>'
                    '<p>On a graph, direct proportion is a straight line through the origin; indirect '
                    'proportion is a curve that gets closer to the axes.</p>'
                ),
                'key_terms': [
                    ('direct proportion', 'both quantities increase or decrease by the same factor; y/x is constant'),
                    ('indirect proportion', 'one quantity increases as the other decreases; x × y is constant'),
                    ('constant of proportionality', 'the fixed value k in y = kx or xy = k'),
                ],
                'example': {
                    'title': 'Worked examples',
                    'html': (
                        '<p><strong>1. Three-part ratio:</strong> Share R1 200 in the ratio 2 : 3 : 5. '
                        'Parts = 10, one part = R120. Shares: <strong>R240, R360, R600</strong>.</p>'
                        '<p><strong>2. Direct:</strong> A car uses 6 litres of petrol for 75 km. How far can it '
                        'go on 10 litres? 75 ÷ 6 = 12,5 km per litre; 12,5 × 10 = <strong>125 km</strong>.</p>'
                        '<p><strong>3. Indirect:</strong> 6 workers build a wall in 10 days. How long would 4 '
                        'workers take? 6 × 10 = 60 worker-days; 60 ÷ 4 = <strong>15 days</strong>.</p>'
                    ),
                },
                'video': {'id': 'a2FZJxl9SjU',
                          'title': 'Grade 9 Maths Proportion (grade 9 direct and inverse proportion) part 1',
                          'channel': 'Miss Martins Maths and Science', 'minutes': 12},
                'worksheet': {
                    'instructions': 'State whether each problem is direct or indirect proportion before you solve it.',
                    'exercises': [
                        '1. Share 180 marbles in the ratio 1 : 2 : 3.',
                        '2. 4 kg of apples cost R58. What do 7 kg cost?',
                        '3. A trip takes 3 hours at 80 km/h. How long does it take at 120 km/h?',
                        '4. 12 learners share a box of sweets and each gets 10. How many would each get if 15 learners shared it?',
                        '5. A printer prints 45 pages in 3 minutes. How many pages in 8 minutes?',
                        '6. Complete the table for indirect proportion (x × y = 36): x = 2, 3, 4, 6, 9; find y.',
                    ],
                },
                'quiz': [
                    ('tf', 'If 3 taps fill a tank in 8 hours, then 6 taps fill it in 4 hours. This is indirect proportion.', True),
                    ('mcq', '5 pens cost R35. What do 8 pens cost?', ['R40', 'R56', 'R48', 'R70'], 1),
                    ('mcq', '6 workers take 10 days. How many days do 4 workers take?',
                     ['15', '8', '12', '6'], 0),
                    ('mcq', 'Share R1 200 in the ratio 2 : 3 : 5. What is the largest share?',
                     ['R500', 'R480', 'R720', 'R600'], 3),
                    ('tf', 'In direct proportion the product x × y stays constant.', False),
                ],
                'homework': {
                    'title': 'Proportion problems',
                    'instructions': 'Solve each problem. Say whether it is direct or indirect proportion.',
                    'tasks': [
                        'A recipe for 4 people needs 300 g of rice. How much rice is needed for 10 people?',
                        'A supply of food lasts 20 days for 9 animals. How long will it last for 12 animals?',
                        'Write your own real-life example of direct proportion and of indirect proportion.',
                    ],
                    'marks': 12,
                },
            },
        ],
    },

    # ======================================================================
    # GRADE 7 NATURAL SCIENCES
    # ======================================================================
    (7, 'NAT-SCI'): {
        'topic': 'The biosphere',
        'caps': 'Life and Living - The biosphere: the concept of the biosphere (lithosphere, hydrosphere, '
                'atmosphere); requirements for sustaining life; the seven life processes '
                '(CAPS Natural Sciences Gr 7, Term 1)',
        'summary': 'Learners meet the four spheres of the Earth, discover what the biosphere needs to '
                   'sustain life, and use the seven life processes to tell living from non-living things.',
        'days': [
            {
                'title': 'The spheres of the Earth',
                'minutes': 50,
                'objectives': [
                    'I can name and describe the lithosphere, hydrosphere, atmosphere and biosphere.',
                    'I can explain that the biosphere overlaps the other three spheres.',
                    'I can give examples of how the spheres interact.',
                ],
                'notes': (
                    '<p>Scientists divide the Earth into four connected parts called <strong>spheres</strong>.</p>'
                    '<ul>'
                    '<li><strong>Lithosphere</strong> (litho = stone): the solid, rocky outer layer of the '
                    'Earth, including rocks, soil and mountains.</li>'
                    '<li><strong>Hydrosphere</strong> (hydro = water): all the water on Earth, in oceans, '
                    'rivers, lakes, groundwater, ice and clouds. About 97% of it is salt water in the oceans.</li>'
                    '<li><strong>Atmosphere</strong> (atmos = vapour): the layer of gases around the Earth. '
                    'It is about 78% nitrogen, 21% oxygen and small amounts of carbon dioxide, argon and '
                    'water vapour.</li>'
                    '<li><strong>Biosphere</strong> (bio = life): all the parts of the Earth where life '
                    'exists, together with all living organisms.</li>'
                    '</ul>'
                    '<p>The biosphere is not a separate layer. It <strong>overlaps</strong> the other three '
                    'spheres: earthworms live in the soil (lithosphere), fish live in water (hydrosphere) and '
                    'birds fly in the air (atmosphere).</p>'
                    '<p>The spheres constantly <strong>interact</strong>. Rain (hydrosphere) falls through '
                    'the air (atmosphere), soaks into soil (lithosphere) and is taken up by plants (biosphere).</p>'
                ),
                'key_terms': [
                    ('lithosphere', 'the rocks and soil of the Earth\'s crust'),
                    ('hydrosphere', 'all the water on Earth'),
                    ('atmosphere', 'the layer of gases surrounding the Earth'),
                    ('biosphere', 'all living things and the parts of the Earth where they live'),
                ],
                'example': {
                    'title': 'Class activity: spot the spheres',
                    'html': (
                        '<p>Look out of the classroom window or at a picture of a river valley. In pairs, make '
                        'a table with four columns: lithosphere, hydrosphere, atmosphere, biosphere.</p>'
                        '<p>List at least two things you can see for each sphere. For example: '
                        '<em>rocks on the riverbank</em> (lithosphere), <em>the river</em> (hydrosphere), '
                        '<em>clouds and wind</em> (atmosphere), <em>trees and birds</em> (biosphere).</p>'
                        '<p>Then write one sentence describing how two spheres interact, e.g. '
                        '"Tree roots break up rocks into soil."</p>'
                    ),
                },
                'video': {'id': '3n3alvzdsUY',
                          'title': "Earth's Four Spheres - Geosphere, Hydrosphere, Atmosphere and Biosphere",
                          'channel': 'Next Generation Science', 'minutes': 5},
                'worksheet': {
                    'instructions': 'Answer the questions in full sentences.',
                    'exercises': [
                        '1. Name the four spheres of the Earth.',
                        '2. Which sphere includes mountains and soil?',
                        '3. Which two gases make up most of the atmosphere? Give their percentages.',
                        '4. Explain why the biosphere is said to overlap the other spheres.',
                        '5. Name one living thing that lives mainly in each of the lithosphere, hydrosphere and atmosphere.',
                        '6. Describe one example of the hydrosphere interacting with the lithosphere.',
                    ],
                },
                'quiz': [
                    ('mcq', 'Which sphere contains all the water on Earth?',
                     ['Lithosphere', 'Atmosphere', 'Hydrosphere', 'Biosphere'], 2),
                    ('mcq', 'Which gas makes up about 78% of the atmosphere?',
                     ['Nitrogen', 'Oxygen', 'Carbon dioxide', 'Argon'], 0),
                    ('tf', 'The biosphere is a separate layer above the atmosphere.', False),
                    ('mcq', 'The word part "litho" means ...', ['life', 'water', 'stone', 'air'], 2),
                ],
                'homework': {
                    'title': 'My spheres poster',
                    'instructions': 'Make a small labelled drawing or poster of a place you know (e.g. your street, a park, a beach).',
                    'tasks': [
                        'Draw the place and label at least one example of each of the four spheres.',
                        'Write two sentences explaining how the spheres in your picture interact.',
                    ],
                    'marks': 10,
                },
            },
            {
                'title': 'Requirements for sustaining life',
                'minutes': 50,
                'objectives': [
                    'I can list the conditions that living things need to survive.',
                    'I can explain why Earth can support life when other planets cannot.',
                    'I can explain how each sphere provides something living things need.',
                ],
                'notes': (
                    '<p>As far as we know, Earth is the only planet that supports life. This is because it '
                    'provides all the <strong>requirements for sustaining life</strong>:</p>'
                    '<ul>'
                    '<li><strong>Water:</strong> all living cells contain water. Water dissolves nutrients and '
                    'carries them around organisms.</li>'
                    '<li><strong>Air (gases):</strong> most organisms need <strong>oxygen</strong> for '
                    'respiration, and plants need <strong>carbon dioxide</strong> to make food.</li>'
                    '<li><strong>Energy from the Sun:</strong> green plants use sunlight to make food. Animals '
                    'get energy by eating plants or other animals.</li>'
                    '<li><strong>Suitable temperature:</strong> most life survives between about 0 °C and '
                    '50 °C. Earth is the right distance from the Sun, and the atmosphere keeps it warm.</li>'
                    '<li><strong>Soil and nutrients:</strong> soil provides minerals for plants and a home for '
                    'many organisms.</li>'
                    '<li><strong>Shelter/habitat:</strong> a place to live that offers protection.</li>'
                    '</ul>'
                    '<p>The atmosphere also protects life: the <strong>ozone layer</strong> absorbs much of '
                    'the Sun\'s harmful ultraviolet (UV) radiation. Mars is too cold and has very little air, '
                    'while Venus is far too hot, so neither can support life as we know it.</p>'
                ),
                'key_terms': [
                    ('sustain', 'to keep something alive or going'),
                    ('habitat', 'the natural home of an organism'),
                    ('ozone layer', 'a layer in the atmosphere that absorbs harmful UV radiation'),
                    ('nutrients', 'substances that organisms need to grow and stay healthy'),
                ],
                'example': {
                    'title': 'Guided activity: design a Moon base',
                    'html': (
                        '<p>The Moon has no air, no liquid water and temperatures from about -170 °C to '
                        '+120 °C. In groups, plan a base where a small garden and people could survive.</p>'
                        '<ol>'
                        '<li>List every requirement for life from today\'s notes.</li>'
                        '<li>For each one, describe how your base would provide it (e.g. tanks of water, '
                        'oxygen supply, heaters and insulation, grow lights).</li>'
                        '<li>Explain which requirement would be the hardest to provide, and why.</li>'
                        '</ol>'
                        '<p>Discuss: what does this show about how special the conditions on Earth are?</p>'
                    ),
                },
                'video': {'id': 'OnCO39YxOfg', 'title': 'Grade 7 - Natural Science - The Biosphere / WorksheetCloud Video Lesson',
                          'channel': 'WorksheetCloud', 'minutes': 8},
                'worksheet': {
                    'instructions': 'Answer the questions in full sentences.',
                    'exercises': [
                        '1. List five requirements for sustaining life on Earth.',
                        '2. Why do plants need carbon dioxide, and why do animals need oxygen?',
                        '3. Explain why water is essential for all living things.',
                        '4. What is the function of the ozone layer?',
                        '5. Give one reason why life as we know it cannot survive on Mars.',
                        '6. Which sphere provides each of these: oxygen, minerals, drinking water?',
                    ],
                },
                'quiz': [
                    ('mcq', 'Which gas do green plants need to make food?',
                     ['Nitrogen', 'Carbon dioxide', 'Oxygen', 'Helium'], 1),
                    ('tf', 'The ozone layer protects living things from harmful UV radiation.', True),
                    ('mcq', 'What is the original source of energy for almost all life on Earth?',
                     ['The Sun', 'The soil', 'Water', 'The Moon'], 0),
                    ('tf', 'Most living things can survive at temperatures of 200 °C.', False),
                ],
                'homework': {
                    'title': 'Life needs',
                    'instructions': 'Choose one plant and one animal that live near your home.',
                    'tasks': [
                        'For each organism, explain how it gets water, energy and the gases it needs.',
                        'Describe the habitat (shelter) of each organism.',
                        'Write one way humans can damage one of these requirements, and one way to protect it.',
                    ],
                    'marks': 12,
                },
            },
            {
                'title': 'The seven life processes',
                'minutes': 50,
                'objectives': [
                    'I can name and describe the seven life processes.',
                    'I can use the life processes to decide whether something is living or non-living.',
                    'I can compare how plants and animals carry out life processes.',
                ],
                'notes': (
                    '<p>All living organisms carry out <strong>seven life processes</strong>. A useful way to '
                    'remember them is <strong>MRS GREN</strong>:</p>'
                    '<ul>'
                    '<li><strong>M - Movement:</strong> moving the whole body or parts of it. Plants move '
                    'slowly, e.g. leaves turning towards light.</li>'
                    '<li><strong>R - Respiration:</strong> releasing energy from food in the cells.</li>'
                    '<li><strong>S - Sensitivity:</strong> sensing and responding to changes in the '
                    'surroundings (light, sound, touch, temperature).</li>'
                    '<li><strong>G - Growth:</strong> increasing in size and becoming more complex.</li>'
                    '<li><strong>R - Reproduction:</strong> producing offspring (young).</li>'
                    '<li><strong>E - Excretion:</strong> getting rid of waste products made in the body, '
                    'e.g. carbon dioxide and urine.</li>'
                    '<li><strong>N - Nutrition:</strong> taking in or making food. Plants make their own food '
                    '(photosynthesis); animals eat other organisms.</li>'
                    '</ul>'
                    '<p>Something is <strong>living</strong> only if it carries out <em>all seven</em> '
                    'processes. A car moves, uses fuel and gives off waste gases, but it does not grow or '
                    'reproduce, so it is <strong>non-living</strong>. A seed looks lifeless but is living: '
                    'when conditions are right it grows and later reproduces.</p>'
                ),
                'key_terms': [
                    ('organism', 'any individual living thing'),
                    ('respiration', 'the release of energy from food inside cells'),
                    ('excretion', 'removing waste products made by the body'),
                    ('sensitivity', 'the ability to detect and respond to changes'),
                ],
                'example': {
                    'title': 'Class activity: living or non-living?',
                    'html': (
                        '<p>Copy the table: list <em>cat, fire, mushroom, robot, cactus, cloud</em> down the side '
                        'and MRS GREN across the top.</p>'
                        '<p>Tick each process the item carries out. Then decide: living or non-living?</p>'
                        '<p><strong>Discussion point:</strong> fire "grows", "moves" and "uses oxygen", but it '
                        'does not reproduce in the biological sense, excrete or have cells, so it is '
                        'non-living. The mushroom is a living fungus: it absorbs food, grows and reproduces '
                        'with spores.</p>'
                    ),
                },
                'video': {'id': 'htjjypdqCkI', 'title': 'MRS GREN | KS3 Biology', 'channel': 'iNewittAll',
                          'minutes': 4},
                'worksheet': {
                    'instructions': 'Answer each question. Use the MRS GREN processes in your answers.',
                    'exercises': [
                        '1. Write out the seven life processes in full.',
                        '2. Describe how a plant shows sensitivity.',
                        '3. What is the difference between nutrition in plants and in animals?',
                        '4. A car moves and uses fuel. Explain why it is not a living thing.',
                        '5. Name two waste products that humans excrete.',
                        '6. Is a dry bean seed living or non-living? Explain.',
                    ],
                },
                'quiz': [
                    ('mcq', 'In MRS GREN, what does the "S" stand for?',
                     ['Sleeping', 'Sensitivity', 'Size', 'Survival'], 1),
                    ('tf', 'An object must carry out all seven life processes to be classed as living.', True),
                    ('mcq', 'Getting rid of waste made in the body is called ...',
                     ['excretion', 'nutrition', 'respiration', 'growth'], 0),
                    ('mcq', 'Which of these is non-living?', ['A mushroom', 'A seed', 'A tree', 'A cloud'], 3),
                ],
                'homework': {
                    'title': 'Life processes at home',
                    'instructions': 'Observe a pet, a garden plant or yourself.',
                    'tasks': [
                        'Give one example of each of the seven life processes for the organism you chose.',
                        'Choose one non-living object at home and explain which life processes it does NOT carry out.',
                    ],
                    'marks': 12,
                },
            },
        ],
    },

    # ======================================================================
    # GRADE 8 NATURAL SCIENCES
    # ======================================================================
    (8, 'NAT-SCI'): {
        'topic': 'Ecosystems: photosynthesis and respiration',
        'caps': 'Life and Living - Photosynthesis and respiration (word equations, products and uses); '
                'interactions and interdependence within the environment (producers, consumers, '
                'decomposers, food chains) (CAPS Natural Sciences Gr 8, Term 1)',
        'summary': 'Learners study how plants make food by photosynthesis, how all living cells release '
                   'energy by respiration, and how the two processes link producers and consumers in an ecosystem.',
        'days': [
            {
                'title': 'Photosynthesis',
                'minutes': 50,
                'objectives': [
                    'I can write the word equation for photosynthesis.',
                    'I can explain the roles of light, chlorophyll, water and carbon dioxide.',
                    'I can describe how plants use and store the glucose they make.',
                ],
                'notes': (
                    '<p>Green plants are <strong>producers</strong>: they make their own food by '
                    '<strong>photosynthesis</strong> (photo = light, synthesis = putting together). It '
                    'happens mainly in the leaves, inside tiny structures called '
                    '<strong>chloroplasts</strong> that contain the green pigment '
                    '<strong>chlorophyll</strong>.</p>'
                    '<p><strong>Word equation:</strong><br>'
                    'carbon dioxide + water &rarr; glucose + oxygen<br>'
                    '<em>(light energy is needed and is absorbed by chlorophyll)</em></p>'
                    '<ul>'
                    '<li><strong>Carbon dioxide</strong> enters the leaf from the air through tiny pores '
                    'called <strong>stomata</strong>.</li>'
                    '<li><strong>Water</strong> is absorbed from the soil by the roots and carried up the stem.</li>'
                    '<li><strong>Light energy</strong> from the Sun is changed into chemical energy stored in glucose.</li>'
                    '<li><strong>Oxygen</strong> is released into the air as a by-product.</li>'
                    '</ul>'
                    '<p>Plants use glucose for energy (respiration) and to build new cells. Extra glucose is '
                    'changed into <strong>starch</strong> and stored in leaves, roots, stems and seeds, e.g. '
                    'potatoes and maize. We can test a leaf for starch with <strong>iodine solution</strong>, '
                    'which turns <strong>blue-black</strong> when starch is present.</p>'
                ),
                'key_terms': [
                    ('photosynthesis', 'the process in which plants use light energy to make glucose from carbon dioxide and water'),
                    ('chlorophyll', 'the green pigment that absorbs light energy'),
                    ('stomata', 'tiny pores in leaves that let gases in and out'),
                    ('starch', 'the form in which plants store extra glucose'),
                ],
                'example': {
                    'title': 'Investigation: testing a leaf for starch (teacher demonstration)',
                    'html': (
                        '<ol>'
                        '<li>Boil a leaf in water for one minute to kill it and soften it.</li>'
                        '<li>Place the leaf in warm ethanol (in a water bath, never over a flame) to remove the chlorophyll. The leaf turns pale.</li>'
                        '<li>Rinse the leaf in warm water and spread it on a white tile.</li>'
                        '<li>Add a few drops of iodine solution.</li>'
                        '</ol>'
                        '<p><strong>Result:</strong> the leaf turns blue-black, showing that starch is present. '
                        'A leaf from a plant kept in the dark for 48 hours stays yellow-brown, which shows '
                        'that <strong>light is needed</strong> for photosynthesis.</p>'
                    ),
                },
                'video': {'id': 'of4tfeaMaqI',
                          'title': 'Gr 8 Natural Science - Photosynthesis and Respiration - Photosynthesis',
                          'channel': 'JuniorTukkie at the University of Pretoria', 'minutes': 10},
                'worksheet': {
                    'instructions': 'Answer the questions in full sentences.',
                    'exercises': [
                        '1. Write the word equation for photosynthesis.',
                        '2. Name the two raw materials (reactants) of photosynthesis and say where each comes from.',
                        '3. What is the function of chlorophyll?',
                        '4. Through which structures does carbon dioxide enter a leaf?',
                        '5. Name two ways plants use the glucose they make.',
                        '6. What colour does iodine solution turn when starch is present?',
                        '7. Why is a plant called a producer?',
                    ],
                },
                'quiz': [
                    ('mcq', 'Which gas is released during photosynthesis?',
                     ['Carbon dioxide', 'Nitrogen', 'Oxygen', 'Hydrogen'], 2),
                    ('mcq', 'Where in a plant cell does photosynthesis take place?',
                     ['Nucleus', 'Chloroplast', 'Cell wall', 'Vacuole'], 1),
                    ('tf', 'Iodine solution turns blue-black when starch is present.', True),
                    ('tf', 'Photosynthesis can take place in complete darkness.', False),
                ],
                'homework': {
                    'title': 'Photosynthesis diagram',
                    'instructions': 'Draw a large labelled diagram of a plant showing photosynthesis.',
                    'tasks': [
                        'Show with labelled arrows where water, carbon dioxide and light enter, and where oxygen leaves.',
                        'Write the word equation under your diagram.',
                        'Name two foods you eat that come from plant starch stores.',
                    ],
                    'marks': 12,
                },
            },
            {
                'title': 'Respiration',
                'minutes': 50,
                'objectives': [
                    'I can write the word equation for respiration.',
                    'I can explain that respiration happens in all living cells, day and night.',
                    'I can tell the difference between respiration and breathing.',
                ],
                'notes': (
                    '<p><strong>Respiration</strong> is the process in which living cells release the energy '
                    'stored in food (glucose). It takes place in every living cell of every organism, '
                    'plants included, all the time, day and night. Most of it happens in tiny structures '
                    'called <strong>mitochondria</strong>.</p>'
                    '<p><strong>Word equation (aerobic respiration):</strong><br>'
                    'glucose + oxygen &rarr; carbon dioxide + water + energy</p>'
                    '<p>Organisms use this energy to move, grow, repair cells, keep warm and carry out all the '
                    'other life processes.</p>'
                    '<p><strong>Respiration is not the same as breathing.</strong> Breathing is the '
                    'physical movement of air into and out of the lungs. It brings oxygen into the body and '
                    'removes carbon dioxide. Respiration is a chemical reaction inside the cells.</p>'
                    '<p>Notice that respiration is the <em>reverse</em> of photosynthesis: the products of '
                    'one are the reactants of the other.</p>'
                    '<p>We can show that we breathe out carbon dioxide using <strong>limewater</strong>: '
                    'blowing through a straw into limewater turns it <strong>milky</strong>.</p>'
                ),
                'key_terms': [
                    ('respiration', 'the chemical process in cells that releases energy from glucose'),
                    ('mitochondria', 'cell structures where most respiration takes place'),
                    ('breathing', 'moving air into and out of the lungs'),
                    ('limewater', 'a solution that turns milky when carbon dioxide is bubbled through it'),
                ],
                'example': {
                    'title': 'Investigation: carbon dioxide in exhaled air',
                    'html': (
                        '<ol>'
                        '<li>Pour clear limewater into two test tubes, A and B.</li>'
                        '<li>Gently <strong>breathe out</strong> through a straw into tube A for about 30 seconds. (Never suck up the liquid.)</li>'
                        '<li>Use a hand pump to bubble ordinary air through tube B for 30 seconds.</li>'
                        '</ol>'
                        '<p><strong>Result:</strong> tube A turns milky quickly; tube B stays clear or turns '
                        'only slightly cloudy.</p>'
                        '<p><strong>Conclusion:</strong> exhaled air contains more carbon dioxide than inhaled '
                        'air, because our cells produce carbon dioxide during respiration.</p>'
                    ),
                },
                'video': {'id': 'JagPP3MX5ks', 'title': 'Cellular Respiration: How Do Cells Get Energy?',
                          'channel': 'Science ABC', 'minutes': 6},
                'worksheet': {
                    'instructions': 'Answer the questions in full sentences.',
                    'exercises': [
                        '1. Write the word equation for respiration.',
                        '2. Where in the cell does most respiration take place?',
                        '3. Do plants respire? When?',
                        '4. Explain the difference between breathing and respiration.',
                        '5. Give three things your body uses the energy from respiration for.',
                        '6. What happens to limewater when you breathe out through it? What does this show?',
                        '7. Compare the reactants and products of photosynthesis and respiration.',
                    ],
                },
                'quiz': [
                    ('mcq', 'Which are the products of respiration?',
                     ['Glucose and oxygen', 'Carbon dioxide, water and energy', 'Starch and oxygen',
                      'Light and water'], 1),
                    ('tf', 'Plants only respire at night.', False),
                    ('tf', 'Breathing and respiration mean exactly the same thing.', False),
                    ('mcq', 'Limewater turns milky in the presence of ...',
                     ['oxygen', 'nitrogen', 'water vapour', 'carbon dioxide'], 3),
                ],
                'homework': {
                    'title': 'Energy for life',
                    'instructions': 'Answer in your exercise book.',
                    'tasks': [
                        'Explain why you breathe faster and deeper when you run.',
                        'Draw a table comparing photosynthesis and respiration: where it happens, reactants, products, when it happens.',
                    ],
                    'marks': 10,
                },
            },
            {
                'title': 'Producers, consumers and the balance of gases',
                'minutes': 50,
                'objectives': [
                    'I can explain how photosynthesis and respiration keep oxygen and carbon dioxide in balance.',
                    'I can classify organisms as producers, consumers or decomposers.',
                    'I can draw a food chain that shows the flow of energy.',
                ],
                'notes': (
                    '<p>Photosynthesis and respiration are linked in a cycle. Plants take in carbon dioxide '
                    'and release oxygen; plants and animals use oxygen in respiration and release carbon '
                    'dioxide. This keeps the levels of these gases in the atmosphere fairly '
                    '<strong>balanced</strong>. Cutting down forests and burning fuels upsets the balance by '
                    'adding more carbon dioxide.</p>'
                    '<p>In an <strong>ecosystem</strong>, organisms depend on one another '
                    '(<strong>interdependence</strong>):</p>'
                    '<ul>'
                    '<li><strong>Producers</strong> (green plants) make food by photosynthesis.</li>'
                    '<li><strong>Consumers</strong> eat other organisms: <em>herbivores</em> eat plants, '
                    '<em>carnivores</em> eat animals and <em>omnivores</em> eat both.</li>'
                    '<li><strong>Decomposers</strong> (bacteria and fungi) break down dead organisms and '
                    'return nutrients to the soil.</li>'
                    '</ul>'
                    '<p>A <strong>food chain</strong> shows how energy passes from one organism to the next. '
                    'The arrow means "is eaten by" and points in the direction energy flows:</p>'
                    '<p>grass &rarr; grasshopper &rarr; lizard &rarr; hawk</p>'
                    '<p>Every food chain starts with a producer, because all the energy originally comes '
                    'from the Sun through photosynthesis. Many linked food chains make a '
                    '<strong>food web</strong>.</p>'
                ),
                'key_terms': [
                    ('ecosystem', 'all the living things in an area interacting with each other and their non-living environment'),
                    ('producer', 'an organism that makes its own food, e.g. a green plant'),
                    ('consumer', 'an organism that eats other organisms for energy'),
                    ('decomposer', 'an organism that breaks down dead material, e.g. fungi and bacteria'),
                    ('interdependence', 'organisms relying on each other to survive'),
                ],
                'example': {
                    'title': 'Worked example: a bushveld food chain',
                    'html': (
                        '<p>acacia tree &rarr; giraffe &rarr; lion</p>'
                        '<ul>'
                        '<li><strong>Producer:</strong> acacia tree (photosynthesis)</li>'
                        '<li><strong>Primary consumer (herbivore):</strong> giraffe</li>'
                        '<li><strong>Secondary consumer (carnivore):</strong> lion</li>'
                        '</ul>'
                        '<p><strong>Gases:</strong> the tree takes in carbon dioxide and gives out oxygen in '
                        'sunlight; all three organisms respire, using oxygen and giving out carbon dioxide.</p>'
                        '<p><strong>What if?</strong> If drought killed many acacia trees, giraffe numbers '
                        'would drop, and then lions would have less food.</p>'
                    ),
                },
                'video': {'id': 'BsVIPnIeYFs', 'title': 'Photosynthesis and Cellular Respiration - Energy Cycle of Life',
                          'channel': 'Point Source Science', 'minutes': 6},
                'worksheet': {
                    'instructions': 'Answer the questions. Draw food chains with arrows pointing in the direction of energy flow.',
                    'exercises': [
                        '1. Explain how photosynthesis and respiration keep oxygen and carbon dioxide in balance.',
                        '2. Classify as producer, herbivore, carnivore, omnivore or decomposer: mushroom, maize, cow, human, leopard.',
                        '3. Draw a food chain with four organisms found in South Africa.',
                        '4. In your food chain, label the producer and the consumers.',
                        '5. Why does every food chain start with a green plant?',
                        '6. What would happen to an ecosystem if all the decomposers disappeared?',
                    ],
                },
                'quiz': [
                    ('mcq', 'In a food chain, the arrow means ...',
                     ['eats', 'is eaten by', 'lives with', 'grows into'], 1),
                    ('mcq', 'Which organism is a decomposer?', ['Grass', 'Hawk', 'Mushroom', 'Rabbit'], 2),
                    ('tf', 'An omnivore eats both plants and animals.', True),
                    ('mcq', 'Which process adds oxygen to the atmosphere?',
                     ['Photosynthesis', 'Respiration', 'Burning fuel', 'Decomposition'], 0),
                ],
                'homework': {
                    'title': 'Garden food web',
                    'instructions': 'Observe a garden, park or open space near your home for 15 minutes.',
                    'tasks': [
                        'List at least six organisms you see (or know live there).',
                        'Draw two food chains using these organisms and link them into a simple food web.',
                        'Explain what would happen if one organism in your web disappeared.',
                    ],
                    'marks': 15,
                },
            },
        ],
    },

    # ======================================================================
    # GRADE 9 NATURAL SCIENCES
    # ======================================================================
    (9, 'NAT-SCI'): {
        'topic': 'Cells as the basic units of life',
        'caps': 'Life and Living - Cells as the basic units of life: cell structure, the microscope, '
                'differences between plant and animal cells, cells in tissues, organs and systems '
                '(CAPS Natural Sciences Gr 9, Term 1)',
        'summary': 'Learners learn that cells are the basic units of life and how microscopes reveal them, '
                   'compare the structures of plant and animal cells, and trace how cells build tissues, '
                   'organs and organ systems.',
        'days': [
            {
                'title': 'Cells and the microscope',
                'minutes': 50,
                'objectives': [
                    'I can explain why the cell is called the basic unit of life.',
                    'I can name the main parts of a light microscope and their functions.',
                    'I can calculate the total magnification of a microscope.',
                ],
                'notes': (
                    '<p>All living organisms are made of one or more <strong>cells</strong>. A cell is the '
                    'smallest unit that can carry out all the life processes, so it is called the '
                    '<strong>basic structural and functional unit of life</strong>.</p>'
                    '<ul>'
                    '<li><strong>Unicellular</strong> organisms consist of one cell (e.g. bacteria, amoeba).</li>'
                    '<li><strong>Multicellular</strong> organisms consist of many cells (e.g. plants, humans).</li>'
                    '</ul>'
                    '<p>In 1665 <strong>Robert Hooke</strong> looked at thin slices of cork under an early '
                    'microscope and named the tiny box-like spaces "cells". Later scientists developed the '
                    '<strong>cell theory</strong>: all living things are made of cells, the cell is the basic '
                    'unit of life, and all cells come from existing cells.</p>'
                    '<p>Most cells are too small to see with the naked eye, so we use a '
                    '<strong>light microscope</strong>. Important parts:</p>'
                    '<ul>'
                    '<li><strong>Eyepiece lens</strong>: the lens you look through (often 10×).</li>'
                    '<li><strong>Objective lenses</strong>: lenses close to the slide (e.g. 4×, 10×, 40×).</li>'
                    '<li><strong>Stage</strong> and <strong>clips</strong>: hold the slide.</li>'
                    '<li><strong>Coarse and fine adjustment knobs</strong>: focus the image.</li>'
                    '<li><strong>Light source / mirror</strong> and <strong>diaphragm</strong>: provide and control light.</li>'
                    '</ul>'
                    '<p><strong>Total magnification = eyepiece magnification × objective magnification.</strong></p>'
                ),
                'key_terms': [
                    ('cell', 'the basic structural and functional unit of all living things'),
                    ('unicellular', 'made of only one cell'),
                    ('multicellular', 'made of many cells'),
                    ('magnification', 'how many times bigger an image is than the real object'),
                ],
                'example': {
                    'title': 'Worked example: magnification',
                    'html': (
                        '<p>A learner uses a 10× eyepiece with a 40× objective lens.</p>'
                        '<p>Total magnification = 10 × 40 = <strong>400×</strong>. The cell appears 400 times '
                        'larger than it really is.</p>'
                        '<p>With the 4× objective: 10 × 4 = <strong>40×</strong>.</p>'
                        '<p><strong>Tip for focusing:</strong> always start with the lowest-power objective and '
                        'use the coarse knob first; then switch to higher power and use only the fine knob, '
                        'so the lens does not crack the slide.</p>'
                    ),
                },
                'video': {'id': 'zcqAD8DBBYU',
                          'title': 'Gr 9 Natural Science - Biology - Cells - Cells as the basic unit of life',
                          'channel': 'JuniorTukkie at the University of Pretoria', 'minutes': 10},
                'worksheet': {
                    'instructions': 'Answer the questions in full sentences.',
                    'exercises': [
                        '1. Why is the cell called the basic unit of life?',
                        '2. Give one example each of a unicellular and a multicellular organism.',
                        '3. Write down the three parts of the cell theory.',
                        '4. What is the function of the fine adjustment knob?',
                        '5. Calculate the total magnification for a 15× eyepiece and a 10× objective.',
                        '6. Why should you start focusing with the lowest-power objective?',
                    ],
                },
                'quiz': [
                    ('mcq', 'Who first used the word "cell" after looking at cork?',
                     ['Charles Darwin', 'Robert Hooke', 'Isaac Newton', 'Louis Pasteur'], 1),
                    ('mcq', 'Eyepiece 10× and objective 40×. What is the total magnification?',
                     ['50×', '4×', '400×', '4 000×'], 2),
                    ('tf', 'A bacterium is a unicellular organism.', True),
                    ('tf', 'According to cell theory, cells can form from non-living matter.', False),
                ],
                'homework': {
                    'title': 'Microscope diagram',
                    'instructions': 'Draw and label a light microscope.',
                    'tasks': [
                        'Draw a light microscope and label at least six parts.',
                        'Next to each label, write the function of that part in a few words.',
                    ],
                    'marks': 12,
                },
            },
            {
                'title': 'Plant and animal cells',
                'minutes': 50,
                'objectives': [
                    'I can identify the main structures of plant and animal cells.',
                    'I can describe the function of each cell structure.',
                    'I can state the differences between plant and animal cells.',
                ],
                'notes': (
                    '<p>Plant and animal cells share several structures:</p>'
                    '<ul>'
                    '<li><strong>Cell membrane</strong>: a thin, flexible layer that surrounds the cell and '
                    'controls what enters and leaves.</li>'
                    '<li><strong>Cytoplasm</strong>: a jelly-like substance where many chemical reactions happen.</li>'
                    '<li><strong>Nucleus</strong>: controls the activities of the cell and contains the '
                    'genetic material (DNA).</li>'
                    '<li><strong>Mitochondria</strong>: where respiration releases energy.</li>'
                    '<li><strong>Vacuoles</strong>: store water and dissolved substances.</li>'
                    '</ul>'
                    '<p>Plant cells also have:</p>'
                    '<ul>'
                    '<li><strong>Cell wall</strong>: a rigid layer of <em>cellulose</em> outside the membrane '
                    'that gives support and shape.</li>'
                    '<li><strong>Chloroplasts</strong>: contain chlorophyll for photosynthesis.</li>'
                    '<li>A <strong>large central vacuole</strong> filled with cell sap that keeps the cell firm.</li>'
                    '</ul>'
                    '<p>Animal cells have no cell wall and no chloroplasts, and usually only small, temporary '
                    'vacuoles. This is why animal cells are often round or irregular, while plant cells are '
                    'more regular and box-shaped.</p>'
                ),
                'key_terms': [
                    ('nucleus', 'the control centre of the cell, containing DNA'),
                    ('cell membrane', 'the layer that controls what enters and leaves the cell'),
                    ('cell wall', 'a rigid cellulose layer around plant cells'),
                    ('chloroplast', 'a structure containing chlorophyll, where photosynthesis happens'),
                    ('cytoplasm', 'the jelly-like substance inside the cell'),
                ],
                'example': {
                    'title': 'Practical: onion and cheek cells (observing and drawing)',
                    'html': (
                        '<p><strong>Onion cells:</strong> peel a thin layer from inside an onion, place it flat '
                        'on a slide, add a drop of iodine, cover with a cover slip and view under 100×. You see '
                        'regular, brick-shaped cells with a clear cell wall and a dark-stained nucleus. '
                        '(Onion skin cells have no chloroplasts because they grow underground.)</p>'
                        '<p><strong>Cheek cells (teacher-led, using a clean cotton bud):</strong> stained with '
                        'methylene blue, they look flat and irregular, with a nucleus but no cell wall.</p>'
                        '<p>Draw one of each with a sharp pencil, label the visible structures and write the '
                        'magnification under the drawing.</p>'
                    ),
                },
                'video': {'id': 'bLeDekGNI_c', 'title': 'KS3 Biology - Animal & Plant Cells', 'channel': 'Cognito',
                          'minutes': 6},
                'worksheet': {
                    'instructions': 'Answer the questions in full sentences.',
                    'exercises': [
                        '1. Name four structures found in both plant and animal cells.',
                        '2. What is the function of the nucleus?',
                        '3. Name three structures found in plant cells but not in animal cells.',
                        '4. What is the cell wall made of, and what is its function?',
                        '5. Why do root cells of a plant have no chloroplasts?',
                        '6. Draw a table to compare plant and animal cells (shape, cell wall, chloroplasts, vacuole).',
                    ],
                },
                'quiz': [
                    ('mcq', 'Which structure is found in plant cells but NOT in animal cells?',
                     ['Nucleus', 'Cell membrane', 'Cytoplasm', 'Cell wall'], 3),
                    ('mcq', 'Which structure controls the activities of the cell?',
                     ['Nucleus', 'Vacuole', 'Cell wall', 'Chloroplast'], 0),
                    ('tf', 'Animal cells have a large central vacuole filled with cell sap.', False),
                    ('mcq', 'In which structure does respiration release energy?',
                     ['Chloroplast', 'Cell wall', 'Mitochondrion', 'Vacuole'], 2),
                ],
                'homework': {
                    'title': 'Cell model plan',
                    'instructions': 'Plan a 3D model of a plant cell or an animal cell using household materials.',
                    'tasks': [
                        'Draw and label the cell you chose, showing all its structures.',
                        'List the household material you would use for each structure (e.g. a plastic bag for the membrane) and explain why.',
                    ],
                    'marks': 12,
                },
            },
            {
                'title': 'Cells, tissues, organs and systems',
                'minutes': 50,
                'objectives': [
                    'I can explain that cells are specialised for different functions.',
                    'I can describe the levels of organisation from cell to organism.',
                    'I can give examples of tissues, organs and organ systems in plants and animals.',
                ],
                'notes': (
                    '<p>In multicellular organisms, cells are <strong>specialised</strong>: their shape and '
                    'structure suit a particular job.</p>'
                    '<ul>'
                    '<li><strong>Red blood cells</strong>: disc-shaped with no nucleus, so they can carry more oxygen.</li>'
                    '<li><strong>Nerve cells</strong>: long and thin, to carry messages over long distances.</li>'
                    '<li><strong>Muscle cells</strong>: can contract (get shorter) to cause movement.</li>'
                    '<li><strong>Root hair cells</strong>: have long extensions that increase the surface for absorbing water.</li>'
                    '</ul>'
                    '<p>Living things are organised in <strong>levels</strong>:</p>'
                    '<ol>'
                    '<li><strong>Cell</strong>: e.g. a muscle cell.</li>'
                    '<li><strong>Tissue</strong>: a group of similar cells doing the same job, e.g. muscle tissue.</li>'
                    '<li><strong>Organ</strong>: different tissues working together, e.g. the heart '
                    '(muscle, nerve and connective tissue).</li>'
                    '<li><strong>Organ system</strong>: organs working together, e.g. the circulatory system '
                    '(heart, blood vessels, blood).</li>'
                    '<li><strong>Organism</strong>: the complete living thing, e.g. a human.</li>'
                    '</ol>'
                    '<p>Plants are organised in the same way: a leaf is an organ made of tissues such as '
                    'epidermis and the tissue that carries out photosynthesis; roots, stems and leaves '
                    'form the plant\'s systems.</p>'
                ),
                'key_terms': [
                    ('specialised cell', 'a cell with a structure adapted to a particular function'),
                    ('tissue', 'a group of similar cells that perform the same function'),
                    ('organ', 'a structure made of different tissues working together'),
                    ('organ system', 'a group of organs that work together to perform a function'),
                ],
                'example': {
                    'title': 'Worked example: levels of organisation',
                    'html': (
                        '<p><strong>Animal:</strong> stomach lining cell &rarr; epithelial tissue &rarr; '
                        'stomach &rarr; digestive system &rarr; human</p>'
                        '<p><strong>Plant:</strong> root hair cell &rarr; root epidermis (tissue) &rarr; root '
                        '(organ) &rarr; root system &rarr; maize plant</p>'
                        '<p><strong>Explain the link:</strong> a red blood cell has a large surface and no '
                        'nucleus, so it can carry a lot of oxygen. Millions together form blood, which is part '
                        'of the circulatory system that delivers oxygen to every cell for respiration.</p>'
                    ),
                },
                'video': {'id': 'PRnK4ys8vm4', 'title': 'Cells Tissues Organs Organ Systems',
                          'channel': 'MooMooMath and Science', 'minutes': 4},
                'worksheet': {
                    'instructions': 'Answer the questions in full sentences.',
                    'exercises': [
                        '1. Write the five levels of organisation in order, from smallest to largest.',
                        '2. What is the difference between a tissue and an organ?',
                        '3. Explain how the shape of a nerve cell suits its function.',
                        '4. Name two organs in the digestive system.',
                        '5. Name one organ in a plant and the tissues it contains.',
                        '6. Arrange in order: heart, cardiac muscle cell, human, circulatory system, cardiac muscle tissue.',
                    ],
                },
                'quiz': [
                    ('mcq', 'A group of similar cells performing the same function is called ...',
                     ['an organ', 'a tissue', 'a system', 'an organism'], 1),
                    ('mcq', 'Which is the correct order?',
                     ['Cell, organ, tissue, system', 'Tissue, cell, organ, system',
                      'Cell, tissue, organ, system', 'Organ, tissue, cell, system'], 2),
                    ('tf', 'The heart is an example of an organ.', True),
                    ('tf', 'Red blood cells have a large nucleus to help them carry oxygen.', False),
                ],
                'homework': {
                    'title': 'Specialised cells',
                    'instructions': 'Research one specialised animal cell and one specialised plant cell (textbook or library).',
                    'tasks': [
                        'Draw each cell and label its special features.',
                        'Explain how each feature helps the cell do its job.',
                        'Name the tissue, organ and system each cell belongs to.',
                    ],
                    'marks': 15,
                },
            },
        ],
    },

    # ======================================================================
    # GRADE 7 ENGLISH HOME LANGUAGE
    # ======================================================================
    (7, 'ENG-HL'): {
        'topic': 'Listening, reading a short story, parts of speech and narrative writing',
        'caps': 'English HL Gr 7 Term 1, Weeks 1-2: listening and speaking (listen to a story, discuss); '
                'reading and viewing (short story: elements of a story); language structures and '
                'conventions (parts of speech: nouns, verbs, adjectives, adverbs, pronouns); writing and '
                'presenting (narrative essay, process writing)',
        'summary': 'Learners listen to and discuss an original short story, identify its elements, revise '
                   'the parts of speech, and plan and draft a narrative essay.',
        'days': [
            {
                'title': 'Listening to and discussing a short story',
                'minutes': 50,
                'objectives': [
                    'I can listen actively and take notes while a story is read aloud.',
                    'I can identify the characters, setting, plot and conflict of a short story.',
                    'I can share my opinion about a story in a group discussion.',
                ],
                'notes': (
                    '<p>Every short story is built from a few key <strong>elements</strong>:</p>'
                    '<ul>'
                    '<li><strong>Characters:</strong> the people (or animals) in the story. The '
                    '<em>main character</em> (protagonist) is the one the story is mostly about.</li>'
                    '<li><strong>Setting:</strong> where and when the story takes place.</li>'
                    '<li><strong>Plot:</strong> the sequence of events: beginning, middle and end.</li>'
                    '<li><strong>Conflict:</strong> the problem or struggle the main character faces.</li>'
                    '<li><strong>Theme:</strong> the message or lesson of the story.</li>'
                    '</ul>'
                    '<p><strong>Active listening</strong> means focusing completely on the speaker. Look at the '
                    'speaker, do not interrupt, jot down key words and think of questions to ask afterwards.</p>'
                    '<p><strong>Story: "The Last Bus"</strong></p>'
                    '<p>Ayanda stared at the clock above the library desk. 17:52. The last bus home left at '
                    'six. She had been so lost in her book that the afternoon had disappeared. Grabbing her '
                    'bag, she raced down the stairs, her shoes slapping the wet pavement. At the corner, an '
                    'old man was struggling to pick up oranges that had spilled from his torn packet. Ayanda '
                    'hesitated. If she stopped, she would miss the bus. She knelt down and helped him gather '
                    'every orange. When she reached the stop, the bus was pulling away. Her heart sank. Then a '
                    'car hooted behind her. It was the old man. "You helped me," he smiled. "Now let me take '
                    'you home."</p>'
                ),
                'key_terms': [
                    ('protagonist', 'the main character of a story'),
                    ('setting', 'the time and place of a story'),
                    ('conflict', 'the problem or struggle in a story'),
                    ('theme', 'the main message or lesson of a story'),
                ],
                'example': {
                    'title': 'Guided class activity: story map',
                    'html': (
                        '<p>Listen while the teacher (or a classmate) reads "The Last Bus" aloud. Then complete '
                        'a story map together:</p>'
                        '<ul>'
                        '<li><strong>Main character:</strong> Ayanda</li>'
                        '<li><strong>Setting:</strong> a library and a street, late on a rainy afternoon</li>'
                        '<li><strong>Conflict:</strong> she must choose between catching the last bus and '
                        'helping a stranger (an inner conflict)</li>'
                        '<li><strong>Resolution:</strong> the old man drives her home</li>'
                        '<li><strong>Theme:</strong> kindness is often repaid</li>'
                        '</ul>'
                        '<p>In groups of four, discuss: Would you have stopped to help? Why or why not? Each '
                        'person speaks once without being interrupted.</p>'
                    ),
                },
                'video': {'id': '4RKXKregWXc',
                          'title': 'Elements of a Short Story | Character, Setting, Plot, Conflict, Resolution, Theme, and Point of View',
                          'channel': 'Learning Language Arts', 'minutes': 8},
                'worksheet': {
                    'instructions': 'Refer to the story "The Last Bus" in the lesson notes. Answer in full sentences.',
                    'exercises': [
                        '1. Who is the main character in the story?',
                        '2. Describe the setting. Give two clues from the text.',
                        '3. Why was Ayanda in a hurry?',
                        '4. What choice did Ayanda have to make? What kind of conflict is this?',
                        '5. How was the conflict resolved?',
                        '6. What is the theme of the story? Explain in your own words.',
                        '7. Find one word in the story that shows sound.',
                    ],
                },
                'quiz': [
                    ('mcq', 'The time and place of a story is called the ...',
                     ['plot', 'theme', 'setting', 'conflict'], 2),
                    ('mcq', 'What is the conflict in "The Last Bus"?',
                     ['Ayanda loses her book', 'Ayanda must choose between the bus and helping someone',
                      'The old man is angry', 'The library closes early'], 1),
                    ('tf', 'An active listener interrupts the speaker often to show interest.', False),
                    ('tf', 'The protagonist is the main character of a story.', True),
                ],
                'homework': {
                    'title': 'Retell a story',
                    'instructions': 'Think of a story a family member has told you, or a favourite story you know.',
                    'tasks': [
                        'Write down the characters, setting, conflict and resolution of the story.',
                        'Practise retelling it aloud in under two minutes, to share in class.',
                    ],
                    'marks': 10,
                },
            },
            {
                'title': 'Parts of speech',
                'minutes': 50,
                'objectives': [
                    'I can identify nouns, pronouns, verbs, adjectives and adverbs in sentences.',
                    'I can identify prepositions and conjunctions.',
                    'I can use the parts of speech correctly in my own sentences.',
                ],
                'notes': (
                    '<p>Every word in a sentence has a job. These jobs are called the '
                    '<strong>parts of speech</strong>.</p>'
                    '<ul>'
                    '<li><strong>Noun:</strong> names a person, place, thing or idea (Ayanda, library, '
                    'orange, kindness). <em>Proper nouns</em> start with a capital letter.</li>'
                    '<li><strong>Pronoun:</strong> takes the place of a noun (she, he, it, they, him, her).</li>'
                    '<li><strong>Verb:</strong> an action or state of being (raced, knelt, is, seemed).</li>'
                    '<li><strong>Adjective:</strong> describes a noun (wet pavement, old man, last bus).</li>'
                    '<li><strong>Adverb:</strong> describes a verb, adjective or another adverb; it often '
                    'tells how, when or where (quickly, yesterday, very).</li>'
                    '<li><strong>Preposition:</strong> shows position or relationship (above, down, at, behind).</li>'
                    '<li><strong>Conjunction:</strong> joins words or clauses (and, but, because, so).</li>'
                    '<li><strong>Interjection:</strong> shows strong feeling (Oh! Wow! Eish!).</li>'
                    '</ul>'
                    '<p>The same word can be different parts of speech depending on its job. In "I '
                    '<em>book</em> a seat", <em>book</em> is a verb; in "I read a <em>book</em>", it is a noun.</p>'
                ),
                'key_terms': [
                    ('noun', 'a naming word'),
                    ('verb', 'a doing or being word'),
                    ('adjective', 'a word that describes a noun'),
                    ('adverb', 'a word that describes a verb, adjective or adverb'),
                    ('preposition', 'a word that shows position or relationship'),
                ],
                'example': {
                    'title': 'Worked example: label every word',
                    'html': (
                        '<p><strong>Sentence:</strong> "The old man smiled warmly at her."</p>'
                        '<ul>'
                        '<li><strong>The</strong> - article (a kind of determiner)</li>'
                        '<li><strong>old</strong> - adjective (describes man)</li>'
                        '<li><strong>man</strong> - noun</li>'
                        '<li><strong>smiled</strong> - verb</li>'
                        '<li><strong>warmly</strong> - adverb (how he smiled)</li>'
                        '<li><strong>at</strong> - preposition</li>'
                        '<li><strong>her</strong> - pronoun (replaces Ayanda)</li>'
                        '</ul>'
                    ),
                },
                'video': {'id': 'chjmnCSPnbw', 'title': 'The 8 Parts of Speech in English Grammar (+ Free PDF & Quiz)',
                          'channel': 'English with Lucy', 'minutes': 15},
                'worksheet': {
                    'instructions': 'Identify the part of speech of each underlined word (written in capitals), or follow the instruction.',
                    'exercises': [
                        '1. Ayanda RACED down the stairs.',
                        '2. The bus left SLOWLY.',
                        '3. She helped the man BECAUSE he needed help.',
                        '4. The library is NEXT TO the post office.',
                        '5. THEY waited in the rain.',
                        '6. Write a sentence with a proper noun, an adjective and an adverb. Label them.',
                        '7. Use the word "light" first as a noun and then as an adjective in two sentences.',
                    ],
                },
                'quiz': [
                    ('mcq', 'In "The tired girl ran home", which word is the adjective?',
                     ['girl', 'ran', 'tired', 'home'], 2),
                    ('mcq', 'Which word is a conjunction?', ['under', 'but', 'quickly', 'happy'], 1),
                    ('tf', 'A pronoun takes the place of a noun.', True),
                    ('mcq', 'In "She sang beautifully", "beautifully" is ...',
                     ['an adverb', 'an adjective', 'a noun', 'a preposition'], 0),
                ],
                'homework': {
                    'title': 'Parts of speech hunt',
                    'instructions': 'Use a newspaper, magazine or book at home.',
                    'tasks': [
                        'Copy one paragraph of about five sentences.',
                        'Underline and label five nouns, five verbs, three adjectives and two adverbs.',
                    ],
                    'marks': 15,
                },
            },
            {
                'title': 'Planning and writing a narrative essay',
                'minutes': 55,
                'objectives': [
                    'I can plan a narrative essay with a clear beginning, middle and end.',
                    'I can write in the first or third person consistently, in the past tense.',
                    'I can use the writing process: plan, draft, edit and rewrite.',
                ],
                'notes': (
                    '<p>A <strong>narrative essay</strong> tells a story. It may be true or imagined. At '
                    'Grade 7 level it is about 150-200 words.</p>'
                    '<p><strong>Structure:</strong></p>'
                    '<ol>'
                    '<li><strong>Introduction:</strong> hook the reader with an interesting opening, and '
                    'introduce the main character and setting.</li>'
                    '<li><strong>Body:</strong> the events build towards a <strong>climax</strong> (the most '
                    'exciting moment). Use a new paragraph for each new event, place or speaker.</li>'
                    '<li><strong>Conclusion:</strong> resolve the conflict and show what the character learnt or felt.</li>'
                    '</ol>'
                    '<p><strong>Tips for a strong narrative:</strong></p>'
                    '<ul>'
                    '<li>Choose one point of view: <em>first person</em> (I, we) or <em>third person</em> '
                    '(he, she, they), and keep to it.</li>'
                    '<li>Write mainly in the <strong>past tense</strong>.</li>'
                    '<li>Use descriptive adjectives and strong verbs ("sprinted" instead of "went fast").</li>'
                    '<li>Include a little dialogue, correctly punctuated with inverted commas.</li>'
                    '<li>Follow the <strong>writing process</strong>: plan (mind map), write a first draft, '
                    'edit for spelling and punctuation, then write a neat final copy.</li>'
                    '</ul>'
                ),
                'key_terms': [
                    ('narrative', 'a piece of writing that tells a story'),
                    ('climax', 'the most exciting or tense point in a story'),
                    ('point of view', 'who tells the story: first person (I) or third person (he/she)'),
                    ('dialogue', 'the words characters speak, placed in inverted commas'),
                ],
                'example': {
                    'title': 'Guided activity: from plan to opening paragraph',
                    'html': (
                        '<p><strong>Topic:</strong> "The day everything went wrong"</p>'
                        '<p><strong>Plan (mind map):</strong> character - me; setting - school sports day; '
                        'conflict - I forgot my running shoes; climax - racing barefoot in the final; '
                        'resolution - I came second and learnt to pack the night before.</p>'
                        '<p><strong>Weak opening:</strong> "One day I went to sports day."</p>'
                        '<p><strong>Strong opening:</strong> "The moment I unzipped my bag, my stomach '
                        'dropped. My running shoes were still at home, under my bed, and the 800 m final was '
                        'in ten minutes."</p>'
                        '<p>Discuss: what makes the second opening better?</p>'
                    ),
                },
                'video': {'id': '-Gl6xqC93RQ', 'title': 'How to Write a Narrative Essay',
                          'channel': 'Hampton Writing Skills Academy', 'minutes': 8},
                'worksheet': {
                    'instructions': 'Plan and begin your narrative essay. Choose ONE topic: "The day everything went wrong", "An unexpected visitor" or "Lost!"',
                    'exercises': [
                        '1. Draw a mind map with your characters, setting, conflict, climax and resolution.',
                        '2. Write down your point of view (first or third person).',
                        '3. Write a strong opening sentence that hooks the reader.',
                        '4. List five strong verbs and five adjectives you plan to use.',
                        '5. Write one line of dialogue with correct punctuation.',
                        '6. Write your first draft of the introduction (one paragraph).',
                    ],
                },
                'quiz': [
                    ('mcq', 'Which tense is a narrative essay usually written in?',
                     ['Future tense', 'Past tense', 'Present continuous', 'No tense'], 1),
                    ('tf', 'The climax is the most exciting point of the story.', True),
                    ('mcq', 'Which is the FIRST step in the writing process?',
                     ['Editing', 'Writing the final copy', 'Planning', 'Publishing'], 2),
                    ('tf', 'It is good practice to switch between first and third person in the same essay.', False),
                ],
                'homework': {
                    'title': 'Narrative essay draft',
                    'instructions': 'Complete the first draft of the narrative essay you planned in class (150-200 words).',
                    'tasks': [
                        'Write the full draft with an introduction, body and conclusion.',
                        'Include at least one line of dialogue.',
                        'Read it aloud to someone at home and correct two mistakes you notice.',
                    ],
                    'marks': 20,
                },
            },
        ],
    },

    # ======================================================================
    # GRADE 8 ENGLISH HOME LANGUAGE
    # ======================================================================
    (8, 'ENG-HL'): {
        'topic': 'Listening and speaking, the short story, sentence structure and descriptive writing',
        'caps': 'English HL Gr 8 Term 1, Weeks 1-2: listening and speaking (listening for comprehension, '
                'conversation); reading and viewing (short story: plot structure, character, conflict); '
                'language structures and conventions (sentences: subject, verb, object; adjectives and '
                'adverbs); writing and presenting (descriptive essay)',
        'summary': 'Learners practise active listening and discussion, analyse the plot structure of an '
                   'original short story, examine sentence structure and descriptive language, and write a '
                   'descriptive essay.',
        'days': [
            {
                'title': 'Active listening and group discussion',
                'minutes': 50,
                'objectives': [
                    'I can use active listening skills during a discussion.',
                    'I can take turns, build on what others say and disagree politely.',
                    'I can summarise the main points of a discussion.',
                ],
                'notes': (
                    '<p>Listening is more than hearing. <strong>Active listening</strong> means paying full '
                    'attention so that you understand, remember and can respond to what someone says.</p>'
                    '<p><strong>Active listening skills:</strong></p>'
                    '<ul>'
                    '<li>Make eye contact and face the speaker.</li>'
                    '<li>Do not interrupt; wait for a natural pause.</li>'
                    '<li>Note key words and ideas.</li>'
                    '<li>Ask questions to clarify ("What did you mean when you said ...?").</li>'
                    '<li><strong>Paraphrase</strong>: repeat the main idea in your own words to check that '
                    'you understood ("So you are saying that ...").</li>'
                    '</ul>'
                    '<p><strong>Group discussion etiquette:</strong></p>'
                    '<ul>'
                    '<li>Take turns and include quieter members.</li>'
                    '<li>Build on others\' ideas: "I agree with Lindiwe, and I would add ..."</li>'
                    '<li>Disagree respectfully: "I see your point, but I think ..."</li>'
                    '<li>Support your opinion with a reason or example.</li>'
                    '</ul>'
                    '<p>One group member acts as <strong>scribe</strong> and summarises the main points at the end.</p>'
                ),
                'key_terms': [
                    ('active listening', 'listening with full attention in order to understand and respond'),
                    ('paraphrase', 'to restate someone\'s idea in your own words'),
                    ('etiquette', 'the polite rules of behaviour in a situation'),
                    ('scribe', 'the person who writes down the group\'s main points'),
                ],
                'example': {
                    'title': 'Class activity: discussion circle',
                    'html': (
                        '<p><strong>Topic:</strong> "Should cellphones be allowed in class?"</p>'
                        '<ol>'
                        '<li>In groups of five, choose a leader (keeps time), a scribe and three speakers.</li>'
                        '<li>Each person has one minute to give an opinion with a reason. Nobody interrupts.</li>'
                        '<li>Before giving your own view, paraphrase the previous speaker in one sentence.</li>'
                        '<li>The scribe summarises the arguments for and against.</li>'
                        '</ol>'
                        '<p><strong>Useful phrases:</strong> "Building on that idea ...", "I respectfully '
                        'disagree because ...", "Could you give an example?"</p>'
                    ),
                },
                'video': {'id': 'i3ku5nx4tMU', 'title': '4 things all great listeners know', 'channel': 'TED-Ed',
                          'minutes': 5},
                'worksheet': {
                    'instructions': 'Answer the questions about listening and discussion skills.',
                    'exercises': [
                        '1. List four things an active listener does.',
                        '2. What does it mean to paraphrase? Give an example.',
                        '3. Rewrite this rude reply politely: "That\'s a stupid idea."',
                        '4. Write two questions you could ask to clarify what a speaker means.',
                        '5. Why is it important to include quieter group members?',
                        '6. Write a three-sentence summary of your group\'s discussion.',
                    ],
                },
                'quiz': [
                    ('tf', 'Paraphrasing means repeating the speaker\'s exact words.', False),
                    ('mcq', 'Which is a polite way to disagree?',
                     ['"You\'re wrong."', '"I see your point, but I think ..."', '"Whatever."',
                      '"That makes no sense."'], 1),
                    ('mcq', 'Which of these is NOT an active listening skill?',
                     ['Making eye contact', 'Asking questions', 'Interrupting to give your view', 'Noting key words'], 2),
                    ('tf', 'Supporting an opinion with a reason makes it more convincing.', True),
                ],
                'homework': {
                    'title': 'Listening log',
                    'instructions': 'Have a five-minute conversation with a family member about a topic that matters to them.',
                    'tasks': [
                        'Use at least two active listening skills during the conversation.',
                        'Write a short paragraph summarising what they said and which skills you used.',
                    ],
                    'marks': 10,
                },
            },
            {
                'title': 'The short story: plot structure',
                'minutes': 50,
                'objectives': [
                    'I can identify the exposition, rising action, climax, falling action and resolution of a story.',
                    'I can describe a character using evidence from the text.',
                    'I can identify internal and external conflict.',
                ],
                'notes': (
                    '<p>Most short stories follow a <strong>plot structure</strong> (often drawn as a '
                    'mountain):</p>'
                    '<ol>'
                    '<li><strong>Exposition:</strong> introduces characters, setting and background.</li>'
                    '<li><strong>Rising action:</strong> complications build tension.</li>'
                    '<li><strong>Climax:</strong> the turning point; the moment of greatest tension.</li>'
                    '<li><strong>Falling action:</strong> events after the climax.</li>'
                    '<li><strong>Resolution:</strong> the conflict is settled.</li>'
                    '</ol>'
                    '<p><strong>Conflict</strong> can be <em>external</em> (character against another person, '
                    'nature or society) or <em>internal</em> (a struggle within the character\'s mind).</p>'
                    '<p><strong>Story: "The Borrowed Bicycle"</strong></p>'
                    '<p>Sizwe had wanted a bicycle for as long as he could remember. When his neighbour, '
                    'Mr Pillay, went away for the weekend, he left his shiny red bicycle against the wall. '
                    '"Just one ride," Sizwe told himself. He flew down the hill, the wind in his ears, until a '
                    'dog darted into the road. Sizwe swerved and crashed into a fence. The front wheel was '
                    'bent. For two days he could not eat or sleep. On Sunday evening, when Mr Pillay\'s car '
                    'pulled in, Sizwe walked over with the bicycle, his hands shaking. "I took it without '
                    'asking," he said. "I am sorry." Mr Pillay was quiet for a long time. Then he said, "You '
                    'will help me fix it on Saturday. And afterwards, you may borrow it - if you ask."</p>'
                ),
                'key_terms': [
                    ('exposition', 'the opening of a story that introduces characters and setting'),
                    ('rising action', 'the events that build tension towards the climax'),
                    ('climax', 'the turning point of the story'),
                    ('resolution', 'how the conflict is finally settled'),
                    ('internal conflict', 'a struggle inside a character\'s mind'),
                ],
                'example': {
                    'title': 'Guided activity: plot mountain for "The Borrowed Bicycle"',
                    'html': (
                        '<ul>'
                        '<li><strong>Exposition:</strong> Sizwe longs for a bicycle; Mr Pillay goes away.</li>'
                        '<li><strong>Rising action:</strong> Sizwe takes the bike, rides down the hill, a dog runs out.</li>'
                        '<li><strong>Climax:</strong> Sizwe confesses to Mr Pillay.</li>'
                        '<li><strong>Falling action:</strong> Mr Pillay\'s long silence.</li>'
                        '<li><strong>Resolution:</strong> they will fix the bike together; Sizwe may borrow it if he asks.</li>'
                        '</ul>'
                        '<p><strong>Discussion:</strong> Some readers see the crash as the climax. Argue for your '
                        'choice with evidence. Note that the crash is an external conflict, but Sizwe\'s guilt is '
                        'an internal conflict.</p>'
                    ),
                },
                'video': {'id': 'G1-MargwX0s', 'title': 'Plot Explained in 2 Minutes #microlearning',
                          'channel': 'Learn It Loud', 'minutes': 2},
                'worksheet': {
                    'instructions': 'Refer to "The Borrowed Bicycle" in the lesson notes. Answer in full sentences.',
                    'exercises': [
                        '1. What do we learn in the exposition?',
                        '2. Name two events in the rising action.',
                        '3. Quote a phrase that shows Sizwe felt guilty.',
                        '4. Identify one external and one internal conflict in the story.',
                        '5. Give two adjectives to describe Mr Pillay, with evidence for each.',
                        '6. What is the theme of the story?',
                        '7. Do you think Mr Pillay\'s response was fair? Give a reason.',
                    ],
                },
                'quiz': [
                    ('mcq', 'The part of the plot that introduces the characters and setting is the ...',
                     ['climax', 'exposition', 'resolution', 'falling action'], 1),
                    ('mcq', 'Sizwe\'s guilt after the crash is an example of ...',
                     ['internal conflict', 'external conflict', 'exposition', 'resolution'], 0),
                    ('tf', 'The climax is the turning point of the story.', True),
                    ('mcq', 'What does Mr Pillay ask Sizwe to do?',
                     ['Pay for a new bicycle', 'Never visit again', 'Help fix the bicycle', 'Apologise to the dog'], 2),
                ],
                'homework': {
                    'title': 'Plot mountain',
                    'instructions': 'Choose a short story, film or TV episode you know well.',
                    'tasks': [
                        'Draw a plot mountain and fill in the five stages with one or two sentences each.',
                        'Identify the main conflict and say whether it is internal or external.',
                    ],
                    'marks': 12,
                },
            },
            {
                'title': 'Sentence structure and descriptive writing',
                'minutes': 55,
                'objectives': [
                    'I can identify the subject, verb and object in a sentence.',
                    'I can use adjectives, adverbs and the five senses to write vivid description.',
                    'I can plan and draft a descriptive essay.',
                ],
                'notes': (
                    '<p><strong>Sentence structure.</strong> A sentence needs a <strong>subject</strong> '
                    '(who or what the sentence is about) and a <strong>verb</strong> (finite verb). Many '
                    'sentences also have an <strong>object</strong> (who or what receives the action).</p>'
                    '<p>Example: <em>Sizwe</em> (subject) <em>fixed</em> (verb) <em>the wheel</em> (object).</p>'
                    '<p><strong>Descriptive essay.</strong> A descriptive essay paints a picture with words of '
                    'a person, place, object or event. Unlike a narrative, it does not need a plot.</p>'
                    '<ul>'
                    '<li>Appeal to all <strong>five senses</strong>: sight, sound, smell, taste and touch.</li>'
                    '<li>Use precise <strong>adjectives</strong> ("crimson", not just "red") and '
                    '<strong>adverbs</strong> ("the wind howled relentlessly").</li>'
                    '<li>Use <strong>figurative language</strong>: similes ("as quiet as a held breath") and '
                    'metaphors ("the market was a beehive").</li>'
                    '<li><strong>Show, don\'t tell:</strong> instead of "It was hot", write "The tar shimmered '
                    'and my shirt stuck to my back."</li>'
                    '<li>Organise paragraphs logically, e.g. from far to near, or sense by sense.</li>'
                    '</ul>'
                ),
                'key_terms': [
                    ('subject', 'the person or thing that does the action of the verb'),
                    ('object', 'the person or thing that receives the action'),
                    ('sensory detail', 'description that appeals to sight, sound, smell, taste or touch'),
                    ('simile', 'a comparison using "like" or "as"'),
                    ('metaphor', 'a comparison that says one thing IS another'),
                ],
                'example': {
                    'title': 'Worked example: improving a description',
                    'html': (
                        '<p><strong>Plain:</strong> "The market was busy. There were lots of fruit and people."</p>'
                        '<p><strong>Improved:</strong> "The Saturday market hummed like a beehive. Bright pyramids '
                        'of mangoes and oranges glowed in the morning sun, and the sweet smell of roasting '
                        'mealies drifted between the stalls. Traders called out prices while shoppers '
                        'squeezed past, shoulder to shoulder."</p>'
                        '<p>Find in the improved version: a simile, two senses other than sight, and a subject + '
                        'verb + object ("Traders called out prices").</p>'
                    ),
                },
                'video': {'id': 'Uy-qqguRrYY',
                          'title': 'Descriptive writing using 5 senses ✍️ | How to write the perfect piece of descriptive writing',
                          'channel': 'Learn Easy English', 'minutes': 6},
                'worksheet': {
                    'instructions': 'Complete the sentence exercises, then plan a descriptive essay on ONE topic: "A storm", "My favourite place" or "The school canteen at break".',
                    'exercises': [
                        '1. Underline the subject and circle the object: The learners cleaned the classroom.',
                        '2. Identify the subject, verb and object: My grandmother bakes delicious bread.',
                        '3. Rewrite with a precise adjective and an adverb: The dog barked.',
                        '4. "Show, don\'t tell": rewrite "I was scared" in two sentences.',
                        '5. For your chosen topic, write one detail for each of the five senses.',
                        '6. Write one simile and one metaphor for your topic.',
                        '7. Write the opening paragraph of your descriptive essay.',
                    ],
                },
                'quiz': [
                    ('mcq', 'In "Lerato kicked the ball", what is the object?',
                     ['Lerato', 'kicked', 'the ball', 'There is no object'], 2),
                    ('mcq', 'Which is a simile?',
                     ['The classroom was a zoo.', 'The wind whispered.', 'Her hands were as cold as ice.',
                      'The sun set.'], 2),
                    ('tf', 'A descriptive essay must always have a plot with a climax.', False),
                    ('tf', '"The smell of fresh bread filled the kitchen" appeals to the sense of smell.', True),
                ],
                'homework': {
                    'title': 'Descriptive essay draft',
                    'instructions': 'Write the first draft of your descriptive essay (200-250 words).',
                    'tasks': [
                        'Use details from all five senses.',
                        'Include at least one simile and one metaphor.',
                        'Underline three sentences where you "show, don\'t tell".',
                    ],
                    'marks': 20,
                },
            },
        ],
    },

    # ======================================================================
    # GRADE 9 ENGLISH HOME LANGUAGE
    # ======================================================================
    (9, 'ENG-HL'): {
        'topic': 'Poetry, sentence types and narrative/descriptive writing',
        'caps': 'English HL Gr 9 Term 1, Weeks 1-2: listening and speaking (reading a poem aloud, '
                'discussion); reading and viewing (poetry: figurative language, sound devices, tone, theme); '
                'language structures and conventions (simple, compound and complex sentences; clauses; '
                'conjunctions); writing and presenting (narrative/descriptive essay)',
        'summary': 'Learners read and analyse an original poem for figurative language and sound devices, '
                   'study simple, compound and complex sentences, and apply both in a narrative or '
                   'descriptive essay.',
        'days': [
            {
                'title': 'Reading poetry: imagery, figurative language and sound',
                'minutes': 55,
                'objectives': [
                    'I can identify similes, metaphors, personification and alliteration in a poem.',
                    'I can explain the effect of a figure of speech or sound device.',
                    'I can describe the tone and theme of a poem.',
                ],
                'notes': (
                    '<p>Poets choose words carefully to create pictures (<strong>imagery</strong>) and sounds.</p>'
                    '<p><strong>Figures of speech:</strong></p>'
                    '<ul>'
                    '<li><strong>Simile:</strong> a comparison using "like" or "as".</li>'
                    '<li><strong>Metaphor:</strong> a direct comparison: one thing <em>is</em> another.</li>'
                    '<li><strong>Personification:</strong> giving human qualities to non-human things.</li>'
                    '<li><strong>Hyperbole:</strong> deliberate exaggeration.</li>'
                    '</ul>'
                    '<p><strong>Sound devices:</strong> <em>alliteration</em> (repeated consonant sounds at '
                    'the start of words), <em>assonance</em> (repeated vowel sounds), <em>onomatopoeia</em> '
                    '(words that imitate sounds) and <em>rhyme</em>.</p>'
                    '<p><strong>Tone</strong> is the poet\'s attitude (e.g. joyful, angry, awed). '
                    '<strong>Theme</strong> is the central message.</p>'
                    '<p><strong>Poem: "Highveld Storm"</strong></p>'
                    '<p>The afternoon holds its breath, heavy and still;<br>'
                    'clouds stack like grey cattle on the hill.<br>'
                    'Then thunder grumbles, gruff and low,<br>'
                    'the wind runs barefoot, to and fro.<br>'
                    'Rain drums the roofs - rat-a-tat-tat -<br>'
                    'the dusty street is a river, wide and flat.<br>'
                    'And when it passes, washed and new,<br>'
                    'the whole sky smiles in borrowed blue.</p>'
                    '<p>When you analyse a device, always say <strong>what</strong> it is, '
                    '<strong>quote</strong> it, and explain its <strong>effect</strong> on the reader.</p>'
                ),
                'key_terms': [
                    ('imagery', 'language that creates pictures in the reader\'s mind'),
                    ('personification', 'giving human qualities to something that is not human'),
                    ('alliteration', 'repetition of the same consonant sound at the start of nearby words'),
                    ('onomatopoeia', 'a word that sounds like the noise it describes'),
                    ('tone', 'the attitude or mood of the speaker in a poem'),
                ],
                'example': {
                    'title': 'Worked example: analysing a line',
                    'html': (
                        '<p><strong>Line:</strong> "clouds stack like grey cattle on the hill"</p>'
                        '<p><strong>What:</strong> a simile (uses "like").</p>'
                        '<p><strong>Effect:</strong> the clouds are compared to cattle crowding together. This '
                        'suggests they are heavy, slow and huge, and it uses a familiar rural image so the '
                        'reader can picture the gathering storm.</p>'
                        '<p><strong>Line:</strong> "thunder grumbles, gruff and low"</p>'
                        '<p><strong>What:</strong> personification (thunder grumbles like a person) and '
                        'alliteration ("grumbles, gruff"). <strong>Effect:</strong> the harsh "g" sounds imitate '
                        'the deep rumble of thunder and make the storm seem bad-tempered.</p>'
                    ),
                },
                'video': {'id': 'NegoYIuXoEA',
                          'title': 'Metaphor, Simile, Personification, Hyperbole | Figurative Language Lesson',
                          'channel': 'Mineola Creative Content', 'minutes': 6},
                'worksheet': {
                    'instructions': 'Refer to the poem "Highveld Storm" in the lesson notes. For each device, name it, quote it and explain its effect.',
                    'exercises': [
                        '1. Quote an example of personification in line 1 and explain it.',
                        '2. Identify the figure of speech in "the dusty street is a river".',
                        '3. Find an example of onomatopoeia. Why is it effective?',
                        '4. Identify the rhyme scheme of the poem.',
                        '5. "the wind runs barefoot" - what does this suggest about the wind?',
                        '6. How does the tone change in the last two lines?',
                        '7. What is the theme of the poem?',
                    ],
                },
                'quiz': [
                    ('mcq', '"The dusty street is a river" is an example of ...',
                     ['simile', 'metaphor', 'onomatopoeia', 'alliteration'], 1),
                    ('mcq', 'Which line contains onomatopoeia?',
                     ['"the whole sky smiles"', '"heavy and still"', '"rat-a-tat-tat"', '"washed and new"'], 2),
                    ('tf', 'Personification gives human qualities to non-human things.', True),
                    ('mcq', 'The repetition of consonant sounds at the start of words is called ...',
                     ['assonance', 'rhyme', 'hyperbole', 'alliteration'], 3),
                ],
                'homework': {
                    'title': 'Weather poem',
                    'instructions': 'Write your own short poem (6-10 lines) about a type of weather.',
                    'tasks': [
                        'Include at least one simile, one metaphor and one example of personification.',
                        'Include one sound device (alliteration or onomatopoeia).',
                        'Underline and label each device you used.',
                    ],
                    'marks': 15,
                },
            },
            {
                'title': 'Simple, compound and complex sentences',
                'minutes': 50,
                'objectives': [
                    'I can identify main (independent) and subordinate (dependent) clauses.',
                    'I can classify sentences as simple, compound or complex.',
                    'I can combine sentences using coordinating and subordinating conjunctions.',
                ],
                'notes': (
                    '<p>A <strong>clause</strong> is a group of words with a subject and a finite verb.</p>'
                    '<ul>'
                    '<li>A <strong>main (independent) clause</strong> makes sense on its own: '
                    '<em>The storm arrived.</em></li>'
                    '<li>A <strong>subordinate (dependent) clause</strong> does not make sense on its own: '
                    '<em>because the wind changed</em>.</li>'
                    '</ul>'
                    '<p><strong>Sentence types:</strong></p>'
                    '<ul>'
                    '<li><strong>Simple:</strong> one main clause. <em>The thunder rumbled.</em></li>'
                    '<li><strong>Compound:</strong> two or more main clauses joined by a coordinating '
                    'conjunction (for, and, nor, but, or, yet, so - remember FANBOYS). '
                    '<em>The thunder rumbled, and the rain began.</em></li>'
                    '<li><strong>Complex:</strong> one main clause and at least one subordinate clause, joined '
                    'by a subordinating conjunction (because, although, when, if, while, until) or a relative '
                    'pronoun (who, which, that). <em>When the thunder rumbled, the children ran inside.</em></li>'
                    '</ul>'
                    '<p>When a subordinate clause comes <em>first</em>, put a comma after it. Good writers '
                    'vary their sentence types: short simple sentences create tension; longer complex ones '
                    'add detail and show how ideas connect.</p>'
                ),
                'key_terms': [
                    ('clause', 'a group of words containing a subject and a finite verb'),
                    ('main clause', 'a clause that makes sense on its own'),
                    ('subordinate clause', 'a clause that depends on a main clause to make sense'),
                    ('coordinating conjunction', 'joins equal clauses: for, and, nor, but, or, yet, so'),
                    ('subordinating conjunction', 'introduces a subordinate clause: because, although, when, if'),
                ],
                'example': {
                    'title': 'Worked example: combining sentences',
                    'html': (
                        '<p><strong>Two simple sentences:</strong> "Thandi studied hard." "She passed the test."</p>'
                        '<p><strong>Compound:</strong> "Thandi studied hard, <em>so</em> she passed the test."</p>'
                        '<p><strong>Complex:</strong> "<em>Because</em> Thandi studied hard, she passed the test." '
                        '(subordinate clause first, so a comma follows it)</p>'
                        '<p><strong>Complex with a relative clause:</strong> "Thandi, <em>who</em> studied hard, '
                        'passed the test."</p>'
                    ),
                },
                'video': {'id': 'smgyeUomfyA', 'title': 'Simple, Compound, Complex Sentences | Learning English',
                          'channel': 'EasyTeaching', 'minutes': 5},
                'worksheet': {
                    'instructions': 'Classify each sentence as simple, compound or complex, or follow the instruction.',
                    'exercises': [
                        '1. The bell rang at eight o\'clock.',
                        '2. I wanted to go to the match, but it was cancelled.',
                        '3. Although it was raining, we walked to school.',
                        '4. The boy who won the race is my cousin.',
                        '5. Underline the subordinate clause: We will start when everyone is seated.',
                        '6. Combine into a compound sentence: The bus was late. We missed assembly.',
                        '7. Combine into a complex sentence using "if": You practise. You will improve.',
                    ],
                },
                'quiz': [
                    ('mcq', '"I was tired, but I finished my homework" is a ... sentence.',
                     ['simple', 'compound', 'complex', 'fragment'], 1),
                    ('mcq', 'Which word is a subordinating conjunction?', ['and', 'but', 'because', 'or'], 2),
                    ('tf', 'A subordinate clause can stand on its own as a complete sentence.', False),
                    ('mcq', 'Which sentence is complex?',
                     ['The dog barked.', 'The dog barked and the cat ran.',
                      'When the dog barked, the cat ran.', 'The dog and the cat ran.'], 2),
                ],
                'homework': {
                    'title': 'Sentence variety',
                    'instructions': 'Take a paragraph you wrote recently (or write a new paragraph of 6 sentences).',
                    'tasks': [
                        'Rewrite it so that it contains at least two simple, two compound and two complex sentences.',
                        'Label each sentence type and underline every subordinate clause.',
                    ],
                    'marks': 12,
                },
            },
            {
                'title': 'Writing a narrative or descriptive essay',
                'minutes': 55,
                'objectives': [
                    'I can choose between a narrative and a descriptive approach for an essay topic.',
                    'I can use "show, don\'t tell", varied sentences and figurative language.',
                    'I can plan, draft and edit an essay of 250-300 words.',
                ],
                'notes': (
                    '<p>In Grade 9 you may be asked to write a <strong>narrative</strong> (tells a story with a '
                    'plot) or a <strong>descriptive</strong> (paints a picture) essay of about 250-300 words. '
                    'Many good essays combine both: a story rich in description.</p>'
                    '<p><strong>Planning:</strong> read the topic carefully, brainstorm ideas, decide on your '
                    'approach and point of view, and draw a paragraph plan (introduction, 3-4 body paragraphs, '
                    'conclusion).</p>'
                    '<p><strong>Techniques that lift your writing:</strong></p>'
                    '<ul>'
                    '<li><strong>Show, don\'t tell:</strong> reveal feelings through actions, senses and '
                    'dialogue ("My hands trembled as I opened the envelope" instead of "I was nervous").</li>'
                    '<li><strong>Vary sentence types:</strong> use a short simple sentence for impact after '
                    'longer complex ones.</li>'
                    '<li><strong>Figurative language:</strong> a few well-chosen similes, metaphors or '
                    'personification, not too many.</li>'
                    '<li><strong>A strong opening</strong> (dialogue, a question, action or a vivid image) and '
                    'a satisfying ending that links back to the beginning.</li>'
                    '</ul>'
                    '<p><strong>Editing checklist:</strong> paragraphing, consistent tense and point of view, '
                    'spelling, punctuation of dialogue, and no run-on sentences.</p>'
                ),
                'key_terms': [
                    ('narrative essay', 'an essay that tells a story with a plot'),
                    ('descriptive essay', 'an essay that creates a vivid picture of a person, place or event'),
                    ('show, don\'t tell', 'revealing feelings and details through actions and senses rather than stating them'),
                    ('run-on sentence', 'two or more main clauses joined without correct punctuation or a conjunction'),
                ],
                'example': {
                    'title': 'Worked example: telling vs showing',
                    'html': (
                        '<p><strong>Topic:</strong> "The moment I will never forget"</p>'
                        '<p><strong>Telling:</strong> "I was very nervous before my speech. It went well and I was happy."</p>'
                        '<p><strong>Showing:</strong> "My notes rustled in my shaking hands. The hall was a sea of '
                        'faces, every one of them waiting. I took a breath. Then I began. When the applause came, '
                        'it rolled over me like a warm wave, and I could not stop grinning."</p>'
                        '<p>Identify: a metaphor, a simile, a short simple sentence used for effect, and a '
                        'complex sentence.</p>'
                    ),
                },
                'video': {'id': 'RSoRzTtwgP4', 'title': 'How to write descriptively - Nalo Hopkinson',
                          'channel': 'TED-Ed', 'minutes': 5},
                'worksheet': {
                    'instructions': 'Choose ONE topic: "The moment I will never forget", "Footsteps in the dark" or "A place that feels like home". Plan your essay.',
                    'exercises': [
                        '1. Decide: narrative, descriptive or a mix? Give a reason for your choice.',
                        '2. Write your point of view and tense.',
                        '3. Draw a paragraph plan (introduction, body paragraphs, conclusion) with one key idea each.',
                        '4. Write two possible opening sentences using different techniques.',
                        '5. Rewrite this "telling" sentence as "showing": "The house was creepy."',
                        '6. Write one complex sentence and one short simple sentence for effect.',
                    ],
                },
                'quiz': [
                    ('tf', 'A descriptive essay focuses on creating a vivid picture rather than telling a plot.', True),
                    ('mcq', 'Which sentence "shows" rather than "tells"?',
                     ['I was angry.', 'She was sad.', 'He slammed the door so hard the windows rattled.',
                      'They were excited.'], 2),
                    ('mcq', 'What length should a Grade 9 essay in this lesson be?',
                     ['50-80 words', '250-300 words', '800-1 000 words', 'One sentence'], 1),
                    ('tf', 'Using as many similes as possible in every sentence always improves an essay.', False),
                ],
                'homework': {
                    'title': 'Essay first draft',
                    'instructions': 'Write the first draft of the essay you planned in class (250-300 words).',
                    'tasks': [
                        'Follow your paragraph plan with a strong opening and a satisfying ending.',
                        'Use at least three "show, don\'t tell" sentences and vary your sentence types.',
                        'Edit your draft with the checklist from the notes and correct at least three errors.',
                    ],
                    'marks': 20,
                },
            },
        ],
    },

    # ======================================================================
    # GRADE 7 isiZulu FIRST ADDITIONAL LANGUAGE
    # ======================================================================
    (7, 'ZUL-FAL'): {
        'topic': 'Izibingelelo nokuzethula (Greetings and introducing yourself)',
        'caps': 'isiZulu FAL Gr 7 Term 1: Ukulalela nokukhuluma - izibingelelo, ukuzethula, imiyalo '
                'yasekilasini; Izakhiwo zolimi - amabizo nezigaba zawo (izigaba 1/2) '
                '(listening and speaking: greetings, introducing oneself, classroom instructions; language: '
                'nouns and noun classes)',
        'summary': 'Learners greet and respond in isiZulu (singular and plural), introduce themselves, '
                   'follow classroom instructions, and meet the noun class system through classes 1 and 2.',
        'days': [
            {
                'title': 'Izibingelelo (Greetings)',
                'minutes': 45,
                'objectives': [
                    'I can greet one person and a group of people in isiZulu.',
                    'I can ask "How are you?" and answer.',
                    'I can say goodbye correctly to someone leaving or staying.',
                ],
                'notes': (
                    '<p>In Zulu culture, greeting is a sign of <strong>inhlonipho</strong> (respect). The '
                    'younger person usually greets first. <em>Sawubona</em> literally means "I see you".</p>'
                    '<ul>'
                    '<li><strong>Sawubona!</strong> - Hello (to one person)</li>'
                    '<li><strong>Sanibonani!</strong> - Hello (to more than one person, or to show respect to an elder)</li>'
                    '<li><strong>Yebo, sawubona.</strong> / <strong>Yebo, sanibonani.</strong> - Yes, hello (reply)</li>'
                    '<li><strong>Unjani?</strong> - How are you? (one person)</li>'
                    '<li><strong>Ninjani?</strong> - How are you? (more than one)</li>'
                    '<li><strong>Ngiyaphila.</strong> - I am well. <strong>Siyaphila.</strong> - We are well.</li>'
                    '<li><strong>Nawe unjani?</strong> - And how are you?</li>'
                    '<li><strong>Ngiyabonga.</strong> - Thank you. <strong>Siyabonga.</strong> - We thank you.</li>'
                    '</ul>'
                    '<p><strong>Saying goodbye</strong> depends on who is leaving:</p>'
                    '<ul>'
                    '<li><strong>Hamba kahle.</strong> - Go well (said <em>to the person who is leaving</em>).</li>'
                    '<li><strong>Sala kahle.</strong> - Stay well (said <em>to the person who stays</em>).</li>'
                    '<li>Plural: <strong>Hambani kahle. / Salani kahle.</strong></li>'
                    '</ul>'
                ),
                'key_terms': [
                    ('Sawubona', 'Hello (to one person)'),
                    ('Sanibonani', 'Hello (to many / respectful)'),
                    ('Unjani?', 'How are you?'),
                    ('Ngiyaphila', 'I am well'),
                    ('Ngiyabonga', 'Thank you'),
                    ('Hamba kahle / Sala kahle', 'Go well / Stay well'),
                ],
                'example': {
                    'title': 'Ingxoxo (Dialogue): Thabo meets Nomsa',
                    'html': (
                        '<p><strong>Thabo:</strong> Sawubona, Nomsa! <em>(Hello, Nomsa!)</em><br>'
                        '<strong>Nomsa:</strong> Yebo, sawubona Thabo. Unjani? <em>(Yes, hello Thabo. How are you?)</em><br>'
                        '<strong>Thabo:</strong> Ngiyaphila, ngiyabonga. Nawe unjani? <em>(I am well, thank you. And you?)</em><br>'
                        '<strong>Nomsa:</strong> Nami ngiyaphila. <em>(I am also well.)</em><br>'
                        '<strong>Thabo:</strong> Kulungile. Sala kahle! <em>(Okay. Stay well!)</em> - Thabo leaves.<br>'
                        '<strong>Nomsa:</strong> Hamba kahle, Thabo! <em>(Go well, Thabo!)</em></p>'
                        '<p>Practise the dialogue in pairs. Then greet a group of three classmates using '
                        '<em>Sanibonani</em> and <em>Ninjani?</em></p>'
                    ),
                },
                'video': {'id': 'A6o5Mrrd4Ww', 'title': 'Learn isiZulu Greetings | How to Greet & Respond in Zulu for Beginners',
                          'channel': 'Zulu Lessons with Thando', 'minutes': 8},
                'worksheet': {
                    'instructions': 'Bhala impendulo efanele. (Write the correct answer.) Give the isiZulu for each phrase, or answer the question.',
                    'exercises': [
                        '1. Greet your teacher. (Hello - respectful/plural form)',
                        '2. Greet your friend. (Hello - one person)',
                        '3. Your friend asks "Unjani?" Answer that you are well and thank them.',
                        '4. How do you ask a group of learners how they are?',
                        '5. Your aunt is leaving your house. What do you say to her?',
                        '6. You are leaving your friend\'s house. What do you say to your friend?',
                        '7. Translate: "We are well, thank you."',
                    ],
                },
                'quiz': [
                    ('mcq', 'How do you greet a group of people?',
                     ['Sawubona', 'Sanibonani', 'Sala kahle', 'Ngiyaphila'], 1),
                    ('mcq', 'What does "Ngiyaphila" mean?',
                     ['Thank you', 'Goodbye', 'I am well', 'How are you?'], 2),
                    ('tf', '"Hamba kahle" is said to the person who is leaving.', True),
                    ('mcq', 'Which phrase means "Thank you"?',
                     ['Ngiyabonga', 'Unjani', 'Yebo', 'Ninjani'], 0),
                ],
                'homework': {
                    'title': 'Greet your family in isiZulu',
                    'instructions': 'Practise the greetings at home.',
                    'tasks': [
                        'Greet two family members in isiZulu and teach them how to reply.',
                        'Write a short dialogue (6 lines) between two friends meeting and saying goodbye, with English translations.',
                    ],
                    'marks': 10,
                },
            },
            {
                'title': 'Ukuzethula (Introducing yourself)',
                'minutes': 45,
                'objectives': [
                    'I can say my name, age and where I live in isiZulu.',
                    'I can ask someone else for this information.',
                    'I can follow basic classroom instructions in isiZulu.',
                ],
                'notes': (
                    '<p><strong>Imibuzo nezimpendulo (Questions and answers):</strong></p>'
                    '<ul>'
                    '<li><strong>Ngubani igama lakho?</strong> - What is your name?<br>'
                    '<strong>Igama lami nguThabo.</strong> / <strong>NginguThabo.</strong> - My name is Thabo. / I am Thabo.</li>'
                    '<li><strong>Uneminyaka emingaki?</strong> - How old are you?<br>'
                    '<strong>Ngineminyaka eyishumi nambili.</strong> - I am twelve years old. '
                    '(eyishumi nantathu = 13)</li>'
                    '<li><strong>Uhlala kuphi?</strong> - Where do you live?<br>'
                    '<strong>Ngihlala eGoli.</strong> - I live in Johannesburg. (eThekwini = in Durban)</li>'
                    '<li><strong>Ufunda ibanga lesingaki?</strong> - Which grade are you in?<br>'
                    '<strong>Ngifunda ibanga lesikhombisa.</strong> - I am in Grade 7.</li>'
                    '</ul>'
                    '<p><strong>Imiyalo yasekilasini (Classroom instructions)</strong> - the -ni ending '
                    'speaks to more than one person:</p>'
                    '<ul>'
                    '<li><strong>Lalelani!</strong> - Listen! <strong>Bhalani!</strong> - Write! '
                    '<strong>Fundani!</strong> - Read!</li>'
                    '<li><strong>Hlalani phansi!</strong> - Sit down! <strong>Sukumani!</strong> - Stand up! '
                    '<strong>Thulani!</strong> - Be quiet!</li>'
                    '</ul>'
                ),
                'key_terms': [
                    ('igama', 'name'),
                    ('iminyaka', 'years (age)'),
                    ('ukuhlala', 'to live / to stay / to sit'),
                    ('ibanga', 'grade (school level)'),
                    ('umfundi / abafundi', 'learner / learners'),
                ],
                'example': {
                    'title': 'Ingxoxo (Dialogue): meeting a new learner',
                    'html': (
                        '<p><strong>Lindiwe:</strong> Sawubona! Ngubani igama lakho? <em>(Hello! What is your name?)</em><br>'
                        '<strong>Peter:</strong> Yebo, sawubona. Igama lami nguPeter. Wena? <em>(Yes, hello. My name is Peter. And you?)</em><br>'
                        '<strong>Lindiwe:</strong> NginguLindiwe. Uneminyaka emingaki? <em>(I am Lindiwe. How old are you?)</em><br>'
                        '<strong>Peter:</strong> Ngineminyaka eyishumi nambili. <em>(I am twelve.)</em><br>'
                        '<strong>Lindiwe:</strong> Uhlala kuphi? <em>(Where do you live?)</em><br>'
                        '<strong>Peter:</strong> Ngihlala eThekwini. <em>(I live in Durban.)</em><br>'
                        '<strong>Lindiwe:</strong> Ngiyajabula ukukwazi! <em>(Nice to meet you!)</em></p>'
                        '<p>In pairs, interview each other with the four questions, then introduce yourself to the class.</p>'
                    ),
                },
                'video': {'id': 'KOSFxtUAc4g',
                          'title': 'How To Introduce Yourself In isiZulu: Perfect Your Greetings & Self-Presentation | ZuluLessons.com',
                          'channel': 'Zulu Lessons with Thando', 'minutes': 8},
                'worksheet': {
                    'instructions': 'Phendula ngesiZulu. (Answer in isiZulu.)',
                    'exercises': [
                        '1. Ngubani igama lakho?',
                        '2. Uneminyaka emingaki?',
                        '3. Uhlala kuphi?',
                        '4. Ufunda ibanga lesingaki?',
                        '5. Translate into English: "Hlalani phansi, nilalele."',
                        '6. Write the isiZulu instruction for "Stand up!" (to the class).',
                        '7. Write three sentences introducing yourself in isiZulu.',
                    ],
                },
                'quiz': [
                    ('mcq', 'What does "Ngubani igama lakho?" mean?',
                     ['Where do you live?', 'What is your name?', 'How old are you?', 'How are you?'], 1),
                    ('mcq', 'How do you say "I live in Durban"?',
                     ['Ngihlala eThekwini', 'NginguThekwini', 'Ngiyaphila eThekwini', 'Hamba eThekwini'], 0),
                    ('tf', '"Bhalani!" means "Write!" (to more than one person).', True),
                    ('mcq', 'Which instruction means "Be quiet!"?', ['Sukumani!', 'Fundani!', 'Thulani!', 'Lalelani!'], 2),
                ],
                'homework': {
                    'title': 'My introduction card',
                    'instructions': 'Make a card that introduces you in isiZulu.',
                    'tasks': [
                        'Write your name, age, where you live and your grade in full isiZulu sentences.',
                        'Add a drawing or photo, and practise saying your introduction aloud for class.',
                    ],
                    'marks': 10,
                },
            },
            {
                'title': 'Amabizo: izigaba 1 no 2 (Nouns: classes 1 and 2)',
                'minutes': 45,
                'objectives': [
                    'I can explain that isiZulu nouns belong to noun classes with prefixes.',
                    'I can change class 1 nouns (um-/umu-) to class 2 plurals (aba-).',
                    'I can use class 1 and 2 nouns in short sentences.',
                ],
                'notes': (
                    '<p>Every isiZulu noun (<strong>ibizo</strong>) belongs to a <strong>noun class</strong> '
                    '(<em>isigaba sebizo</em>). The class is shown by the <strong>prefix</strong> at the '
                    'start of the noun. Singular and plural nouns are usually in different classes.</p>'
                    '<p><strong>Class 1 (singular): um- / umu-</strong> &nbsp; <strong>Class 2 (plural): aba-</strong><br>'
                    'Classes 1 and 2 are mostly for <strong>people</strong>.</p>'
                    '<ul>'
                    '<li>umuntu (person) &rarr; abantu (people)</li>'
                    '<li>umfana (boy) &rarr; abafana (boys)</li>'
                    '<li>umfundi (learner) &rarr; abafundi (learners)</li>'
                    '<li>umngane (friend) &rarr; abangane (friends)</li>'
                    '<li>umntwana (child) &rarr; abantwana (children)</li>'
                    '</ul>'
                    '<p><strong>Class 1a / 2a: u- &rarr; o-</strong> (family words and names):<br>'
                    'umama (mother) &rarr; omama; ubaba (father) &rarr; obaba; ugogo (grandmother) &rarr; ogogo.</p>'
                    '<p>Notice: the beginning of the verb changes to agree with the noun. '
                    '<strong>Umfana uyadlala</strong> (The boy is playing) but '
                    '<strong>Abafana bayadlala</strong> (The boys are playing).</p>'
                ),
                'key_terms': [
                    ('ibizo / amabizo', 'noun / nouns'),
                    ('isiqalo', 'prefix (beginning part of a word)'),
                    ('ubunye', 'singular'),
                    ('ubuningi', 'plural'),
                ],
                'example': {
                    'title': 'Guided activity: singular to plural',
                    'html': (
                        '<p>The teacher says a singular noun; the class answers with the plural and an English meaning.</p>'
                        '<p><strong>Thisha:</strong> umfundi! &nbsp; <strong>Abafundi:</strong> abafundi - learners!<br>'
                        '<strong>Thisha:</strong> umngane! &nbsp; <strong>Abafundi:</strong> abangane - friends!</p>'
                        '<p>Then change the sentence to plural:</p>'
                        '<p><strong>Umfundi uyafunda.</strong> (The learner is reading.) &rarr; '
                        '<strong>Abafundi bayafunda.</strong> (The learners are reading.)</p>'
                        '<p><strong>Umntwana uyadla.</strong> (The child is eating.) &rarr; '
                        '<strong>Abantwana bayadla.</strong> (The children are eating.)</p>'
                    ),
                },
                'video': {'id': 'JY9nKkObqJs',
                          'title': "Learn isiZulu Easily: Beginner's Guide To Noun Classes & Their Formation | ZuluLessons.com",
                          'channel': 'Zulu Lessons with Thando', 'minutes': 10},
                'worksheet': {
                    'instructions': 'Bhala ubuningi. (Write the plural.) Then give the English meaning.',
                    'exercises': [
                        '1. umuntu',
                        '2. umfana',
                        '3. umngane',
                        '4. umama',
                        '5. ugogo',
                        '6. Change to plural: Umfana uyadlala.',
                        '7. Change to plural: Umfundi uyabhala.',
                    ],
                },
                'quiz': [
                    ('mcq', 'What is the plural of "umfana"?', ['imifana', 'abafana', 'amafana', 'izifana'], 1),
                    ('mcq', 'What is the plural of "umama"?', ['abamama', 'imimama', 'omama', 'amama'], 2),
                    ('tf', 'Class 1 and 2 nouns are mostly used for people.', True),
                    ('mcq', 'What does "Abantwana bayadla" mean?',
                     ['The children are eating.', 'The child is eating.', 'The children are playing.',
                      'The people are reading.'], 0),
                ],
                'homework': {
                    'title': 'People nouns',
                    'instructions': 'Use the nouns from today\'s lesson.',
                    'tasks': [
                        'Write five class 1 nouns with their class 2 plurals and English meanings.',
                        'Write two sentences in the singular and change them to the plural.',
                    ],
                    'marks': 10,
                },
            },
        ],
    },

    # ======================================================================
    # GRADE 8 isiZulu FIRST ADDITIONAL LANGUAGE
    # ======================================================================
    (8, 'ZUL-FAL'): {
        'topic': 'Ukwethula abanye nokufunda umbhalo omfushane (Introducing others and reading a short text)',
        'caps': 'isiZulu FAL Gr 8 Term 1: Ukulalela nokukhuluma - izibingelelo, ukuzethula nokwethula abanye, '
                'ingxoxo; Ukufunda nokubuka - ukufunda nokuqonda umbhalo omfushane; Izakhiwo zolimi - '
                'izigaba zamabizo 1-10 (introducing self and others, conversation, comprehension of a '
                'short text, noun classes)',
        'summary': 'Learners revise greetings, introduce themselves and others, read and answer questions '
                   'on a short isiZulu text, and work with singular and plural forms of noun classes 1-10.',
        'days': [
            {
                'title': 'Ukwethula abanye (Introducing others)',
                'minutes': 45,
                'objectives': [
                    'I can greet respectfully and introduce myself in isiZulu.',
                    'I can introduce a friend or family member to someone else.',
                    'I can respond politely when someone is introduced to me.',
                ],
                'notes': (
                    '<p><strong>Revision:</strong> Sawubona / Sanibonani - Unjani? / Ninjani? - Ngiyaphila, '
                    'ngiyabonga. Use <em>Sanibonani</em> for elders to show respect (inhlonipho).</p>'
                    '<p><strong>Introducing yourself:</strong></p>'
                    '<ul>'
                    '<li><strong>NginguSipho.</strong> - I am Sipho.</li>'
                    '<li><strong>Ngineminyaka eyishumi nantathu.</strong> - I am thirteen years old.</li>'
                    '<li><strong>Ngifunda ibanga lesishiyagalombili.</strong> - I am in Grade 8.</li>'
                    '</ul>'
                    '<p><strong>Introducing someone else</strong> - use <em>lo</em> (this, for one person) or '
                    '<em>laba</em> (these, for people):</p>'
                    '<ul>'
                    '<li><strong>Lo ngumngane wami, uZanele.</strong> - This is my friend, Zanele.</li>'
                    '<li><strong>Lo ngumama wami.</strong> - This is my mother.</li>'
                    '<li><strong>Laba ngabangane bami.</strong> - These are my friends.</li>'
                    '<li><strong>Uhlala eSoweto.</strong> - She/He lives in Soweto.</li>'
                    '</ul>'
                    '<p><strong>Responding:</strong></p>'
                    '<ul>'
                    '<li><strong>Ngiyajabula ukukwazi.</strong> - I am pleased to meet you.</li>'
                    '<li><strong>Nami ngiyajabula.</strong> - I am pleased too.</li>'
                    '</ul>'
                ),
                'key_terms': [
                    ('ukwethula', 'to introduce'),
                    ('lo / laba', 'this (person) / these (people)'),
                    ('umngane wami', 'my friend'),
                    ('Ngiyajabula ukukwazi', 'Pleased to meet you'),
                    ('inhlonipho', 'respect'),
                ],
                'example': {
                    'title': 'Ingxoxo (Dialogue): Sipho introduces Zanele to his gogo',
                    'html': (
                        '<p><strong>Sipho:</strong> Sanibonani, Gogo. <em>(Hello, Grandmother.)</em><br>'
                        '<strong>Gogo:</strong> Yebo, sawubona mzukulu. Unjani? <em>(Yes, hello grandchild. How are you?)</em><br>'
                        '<strong>Sipho:</strong> Ngiyaphila, Gogo. Lo ngumngane wami, uZanele. <em>(I am well, Grandmother. This is my friend, Zanele.)</em><br>'
                        '<strong>Zanele:</strong> Sanibonani, Gogo. Ngiyajabula ukunazi. <em>(Hello, Grandmother. I am pleased to meet you.)</em><br>'
                        '<strong>Gogo:</strong> Nami ngiyajabula, Zanele. Uhlala kuphi? <em>(I am pleased too, Zanele. Where do you live?)</em><br>'
                        '<strong>Zanele:</strong> Ngihlala eSoweto. <em>(I live in Soweto.)</em></p>'
                        '<p><em>Note:</em> Zanele says <strong>ukunazi</strong> (the plural form) to show respect to an elder.</p>'
                        '<p>In groups of three, take turns introducing one member to another.</p>'
                    ),
                },
                'video': {'id': '8RKuM-wXDeA', 'title': 'ISIZULU LESSON NO3 INTRODUCING YOURSELF AND OTHERS',
                          'channel': 'Code Switching 2020', 'minutes': 8},
                'worksheet': {
                    'instructions': 'Bhala ngesiZulu. (Write in isiZulu.)',
                    'exercises': [
                        '1. Greet an elder respectfully.',
                        '2. Introduce yourself: name, age and grade.',
                        '3. Introduce your friend Themba to your teacher.',
                        '4. Introduce your mother to a friend.',
                        '5. How do you say "These are my friends"?',
                        '6. Someone says "Ngiyajabula ukukwazi." How do you reply?',
                        '7. Translate into English: "Lo ngumngane wami. Uhlala eThekwini."',
                    ],
                },
                'quiz': [
                    ('mcq', 'How do you say "This is my friend"?',
                     ['Laba ngabangane bami', 'Lo ngumngane wami', 'NgingumNgane', 'Sala kahle mngane'], 1),
                    ('mcq', 'What does "Ngiyajabula ukukwazi" mean?',
                     ['I am pleased to meet you', 'I am going home', 'I know you are well', 'Thank you very much'], 0),
                    ('tf', '"Laba" is used when introducing more than one person.', True),
                    ('tf', 'It is respectful to greet an elder with "Sanibonani".', True),
                ],
                'homework': {
                    'title': 'Introduce my family',
                    'instructions': 'Draw or paste a picture of three family members or friends.',
                    'tasks': [
                        'Introduce each person in one or two isiZulu sentences (e.g. Lo ngumama wami. Uhlala eGoli.).',
                        'Write English translations underneath.',
                    ],
                    'marks': 12,
                },
            },
            {
                'title': 'Ukufunda nokuqonda (Reading for understanding)',
                'minutes': 45,
                'objectives': [
                    'I can read a short isiZulu text aloud with correct pronunciation.',
                    'I can find information in the text to answer questions.',
                    'I can learn new words from context.',
                ],
                'notes': (
                    '<p><strong>Reading strategies:</strong> read the title and guess what the text is '
                    'about; read once for the general idea; read again slowly and underline words you do not '
                    'know; use the words around them (context) to guess the meaning.</p>'
                    '<p><strong>Umbhalo: "USipho"</strong></p>'
                    '<p>USipho ungumfundi webanga lesishiyagalombili. Uneminyaka eyishumi nantathu. Uhlala '
                    'eThekwini nomama wakhe nodadewabo omncane. Njalo ekuseni uvuka ngo-6. Udla ukudla '
                    'kwasekuseni, bese ehamba ngezinyawo eya esikoleni. Isifundo asithanda kakhulu yizibalo. '
                    'Emva kwesikole udlala ibhola nabangane bakhe. Ebusuku wenza umsebenzi wesikole, bese '
                    'elala ngo-9.</p>'
                    '<p><strong>Amagama amasha (New words):</strong></p>'
                    '<ul>'
                    '<li><strong>ekuseni</strong> - in the morning; <strong>ebusuku</strong> - at night</li>'
                    '<li><strong>uvuka</strong> - he wakes up; <strong>ulala</strong> - he sleeps</li>'
                    '<li><strong>ukudla kwasekuseni</strong> - breakfast</li>'
                    '<li><strong>ehamba ngezinyawo</strong> - walking (on foot)</li>'
                    '<li><strong>izibalo</strong> - mathematics</li>'
                    '<li><strong>udadewabo omncane</strong> - his younger sister</li>'
                    '</ul>'
                ),
                'key_terms': [
                    ('umbhalo', 'text / piece of writing'),
                    ('ukufunda', 'to read / to learn'),
                    ('ukuqonda', 'to understand'),
                    ('umbuzo / imibuzo', 'question / questions'),
                    ('impendulo', 'answer'),
                ],
                'example': {
                    'title': 'Guided reading: answering questions from the text',
                    'html': (
                        '<p>Read "USipho" aloud together. Then look at how to answer in a full sentence, using '
                        'words from the text:</p>'
                        '<p><strong>Umbuzo:</strong> USipho uhlala kuphi? <em>(Where does Sipho live?)</em><br>'
                        '<strong>Impendulo:</strong> USipho uhlala eThekwini. <em>(Sipho lives in Durban.)</em></p>'
                        '<p><strong>Umbuzo:</strong> USipho uya kanjani esikoleni? <em>(How does Sipho go to school?)</em><br>'
                        '<strong>Impendulo:</strong> Uhamba ngezinyawo. <em>(He walks.)</em></p>'
                        '<p>Tip: the question word tells you what to look for - <em>kuphi?</em> (where), '
                        '<em>nini?</em> (when), <em>kanjani?</em> (how), <em>ubani?</em> (who), '
                        '<em>malini?</em> (how much).</p>'
                    ),
                },
                'video': {'id': '61GPzA3O_V4', 'title': 'Ukufunda Nokuqondisisa', 'channel': 'IsiZulu with Teacher Zeey',
                          'minutes': 8},
                'worksheet': {
                    'instructions': 'Funda umbhalo "USipho" bese uphendula imibuzo. (Read the text "USipho" and answer the questions in full sentences.)',
                    'exercises': [
                        '1. USipho ufunda ibanga lesingaki?',
                        '2. USipho uneminyaka emingaki?',
                        '3. USipho uhlala nobani?',
                        '4. USipho uvuka ngasikhathi sini ekuseni?',
                        '5. Isifundo asithanda kakhulu yisiphi?',
                        '6. Wenzani emva kwesikole?',
                        '7. Translate into English: "Ebusuku wenza umsebenzi wesikole."',
                    ],
                },
                'quiz': [
                    ('mcq', 'Where does Sipho live?', ['eGoli', 'eThekwini', 'eSoweto', 'ePitoli'], 1),
                    ('mcq', 'Which subject does Sipho like most?',
                     ['IsiNgisi', 'Izibalo', 'Isayensi', 'Umlando'], 1),
                    ('tf', 'Sipho goes to school by bus.', False),
                    ('mcq', 'What does "ebusuku" mean?', ['In the morning', 'At night', 'At school', 'After school'], 1),
                ],
                'homework': {
                    'title': 'My day',
                    'instructions': 'Use the text "USipho" as a model.',
                    'tasks': [
                        'Write 5-6 isiZulu sentences about your own day (when you wake up, how you go to school, your favourite subject, what you do after school).',
                        'Read your text aloud to someone at home.',
                    ],
                    'marks': 12,
                },
            },
            {
                'title': 'Izigaba zamabizo 1-10 (Noun classes 1-10)',
                'minutes': 45,
                'objectives': [
                    'I can identify the prefixes of noun classes 1 to 10.',
                    'I can form the plural of nouns in classes 1, 3, 5, 7 and 9.',
                    'I can sort nouns into their correct classes.',
                ],
                'notes': (
                    '<p>isiZulu nouns are grouped into classes by their <strong>prefix</strong>. Odd-numbered '
                    'classes are usually singular and the next even class is the plural.</p>'
                    '<ul>'
                    '<li><strong>Class 1 um(u)- &rarr; Class 2 aba-:</strong> umuntu &rarr; abantu (person/people); '
                    'umfundi &rarr; abafundi (learner/s)</li>'
                    '<li><strong>Class 3 um(u)- &rarr; Class 4 imi-:</strong> umuthi &rarr; imithi (tree/s); '
                    'umfula &rarr; imifula (river/s)</li>'
                    '<li><strong>Class 5 i(li)- &rarr; Class 6 ama-:</strong> iqanda &rarr; amaqanda (egg/s); '
                    'ihhashi &rarr; amahhashi (horse/s)</li>'
                    '<li><strong>Class 7 isi- &rarr; Class 8 izi-:</strong> isikole &rarr; izikole (school/s); '
                    'isitsha &rarr; izitsha (dish/es)</li>'
                    '<li><strong>Class 9 i(n)- &rarr; Class 10 izi(n)-:</strong> inja &rarr; izinja (dog/s); '
                    'indlu &rarr; izindlu (house/s)</li>'
                    '</ul>'
                    '<p>Classes 1 and 3 have the <em>same</em> prefix um(u)-, but class 1 is for people and '
                    'class 3 is mostly for things like trees, rivers and body parts (umlomo - mouth). You can '
                    'tell them apart by their plurals: aba- (people) or imi- (things).</p>'
                ),
                'key_terms': [
                    ('isigaba', 'class (group)'),
                    ('isiqalo', 'prefix'),
                    ('ubunye / ubuningi', 'singular / plural'),
                    ('umsuka', 'stem (root of the word)'),
                ],
                'example': {
                    'title': 'Guided activity: sort the nouns',
                    'html': (
                        '<p>Write these nouns on cards: <em>umfana, umuthi, iqanda, isitsha, inja, umfula, '
                        'isikole, indlu</em>.</p>'
                        '<p>In groups, sort them into classes 1, 3, 5, 7 and 9 and write the plural of each.</p>'
                        '<p><strong>Answers:</strong> Class 1: umfana &rarr; abafana. Class 3: umuthi &rarr; imithi, '
                        'umfula &rarr; imifula. Class 5: iqanda &rarr; amaqanda. Class 7: isitsha &rarr; izitsha, '
                        'isikole &rarr; izikole. Class 9: inja &rarr; izinja, indlu &rarr; izindlu.</p>'
                    ),
                },
                'video': {'id': 'RT3Xo5o2WjE', 'title': 'IsiZulu Noun Classes explained!',
                          'channel': 'Zamani Zulu - Learn isiZulu', 'minutes': 10},
                'worksheet': {
                    'instructions': 'Bhala ubuningi bala mabizo bese ubhala isigaba. (Write the plural and the class number of the singular noun.)',
                    'exercises': [
                        '1. umfundi',
                        '2. umfula',
                        '3. iqanda',
                        '4. isikole',
                        '5. inja',
                        '6. indlu',
                        '7. Explain the difference between class 1 and class 3 nouns.',
                    ],
                },
                'quiz': [
                    ('mcq', 'What is the plural of "isikole"?', ['amakole', 'izikole', 'imikole', 'abakole'], 1),
                    ('mcq', 'What is the plural of "umuthi" (tree)?', ['abathi', 'amathi', 'imithi', 'izithi'], 2),
                    ('mcq', 'Which class prefix is "ama-"?', ['Class 6', 'Class 2', 'Class 4', 'Class 8'], 0),
                    ('tf', '"Izinja" is the plural of "inja".', True),
                ],
                'homework': {
                    'title': 'Noun class chart',
                    'instructions': 'Make a chart of noun classes 1-10.',
                    'tasks': [
                        'For each pair of classes (1/2, 3/4, 5/6, 7/8, 9/10) write the prefixes and two example nouns with plurals.',
                        'Add the English meaning of every noun.',
                    ],
                    'marks': 15,
                },
            },
        ],
    },

    # ======================================================================
    # GRADE 9 isiZulu FIRST ADDITIONAL LANGUAGE
    # ======================================================================
    (9, 'ZUL-FAL'): {
        'topic': 'Ingxoxo, ukufunda nokuqonda nezabizwana (Conversation, comprehension and pronouns)',
        'caps': 'isiZulu FAL Gr 9 Term 1: Ukulalela nokukhuluma - ingxoxo (izibingelelo, ukuzethula '
                'nokwethula abanye); Ukufunda nokubuka - ukufunda nokuqonda umbhalo omfushane; Izakhiwo '
                'zolimi - izabizwana zoqobo (conversation, comprehension of a short text, absolute pronouns)',
        'summary': 'Learners hold a short conversation with greetings and introductions, read and respond '
                   'to a short text about a first school day, and learn the absolute pronouns (izabizwana zoqobo).',
        'days': [
            {
                'title': 'Ingxoxo: ukuzethula ngokugcwele (Conversation: introducing yourself fully)',
                'minutes': 45,
                'objectives': [
                    'I can take part in a short conversation using greetings and introductions.',
                    'I can talk about my family, my hobbies and my school subjects.',
                    'I can ask follow-up questions in isiZulu.',
                ],
                'notes': (
                    '<p><strong>Revision of greetings:</strong> Sawubona/Sanibonani - Unjani?/Ninjani? - '
                    'Ngiyaphila, ngiyabonga. Nawe unjani?</p>'
                    '<p><strong>Talking about yourself:</strong></p>'
                    '<ul>'
                    '<li><strong>Ngineminyaka eyishumi nane.</strong> - I am fourteen years old.</li>'
                    '<li><strong>Ngifunda ibanga lesishiyagalolunye.</strong> - I am in Grade 9.</li>'
                    '<li><strong>Ngihlala nomama nobaba.</strong> - I live with my mother and father.</li>'
                    '<li><strong>Nginabafowethu ababili.</strong> - I have two brothers.</li>'
                    '<li><strong>Ngithanda ukudlala ibhola / ukufunda / ukucula.</strong> - I like playing soccer / reading / singing.</li>'
                    '<li><strong>Isifundo engisithandayo yisiNgisi.</strong> - My favourite subject is English.</li>'
                    '</ul>'
                    '<p><strong>Follow-up questions:</strong></p>'
                    '<ul>'
                    '<li><strong>Uthanda ukwenzani?</strong> - What do you like to do?</li>'
                    '<li><strong>Uhlala nobani?</strong> - Who do you live with?</li>'
                    '<li><strong>Isifundo osithandayo yisiphi?</strong> - Which subject do you like?</li>'
                    '<li><strong>Kungani?</strong> - Why?</li>'
                    '</ul>'
                    '<p>A good conversation has a greeting, questions <em>and</em> answers from both '
                    'speakers, and a polite ending (<em>Kuhle ukukwazi. Sala kahle!</em> - It was nice to meet you. Stay well!).</p>'
                ),
                'key_terms': [
                    ('ingxoxo', 'conversation / dialogue'),
                    ('umndeni', 'family'),
                    ('ukuthanda', 'to like / to love'),
                    ('Kungani?', 'Why?'),
                    ('isifundo', 'school subject / lesson'),
                ],
                'example': {
                    'title': 'Ingxoxo (Dialogue): two new classmates',
                    'html': (
                        '<p><strong>Ayanda:</strong> Sawubona! Ngingu-Ayanda. Wena ungubani? <em>(Hello! I am Ayanda. Who are you?)</em><br>'
                        '<strong>Kevin:</strong> Yebo, sawubona. NginguKevin. Ngiyajabula ukukwazi. <em>(Yes, hello. I am Kevin. Pleased to meet you.)</em><br>'
                        '<strong>Ayanda:</strong> Nami. Uthanda ukwenzani? <em>(Me too. What do you like to do?)</em><br>'
                        '<strong>Kevin:</strong> Ngithanda ukudlala ibhola nokufunda. Wena? <em>(I like playing soccer and reading. And you?)</em><br>'
                        '<strong>Ayanda:</strong> Mina ngithanda ukucula. Isifundo osithandayo yisiphi? <em>(I like singing. Which subject do you like?)</em><br>'
                        '<strong>Kevin:</strong> Yizibalo. <em>(Mathematics.)</em> &nbsp; <strong>Ayanda:</strong> Kungani? <em>(Why?)</em><br>'
                        '<strong>Kevin:</strong> Ngoba zilula kimi! <em>(Because it is easy for me!)</em></p>'
                        '<p>In pairs, hold your own 2-minute conversation. Each person must ask at least three questions.</p>'
                    ),
                },
                'video': {'id': 'ZJyCnTVKGmc',
                          'title': 'Learn isiZulu: How to Introduce Yourself Fully (Name, Siblings, Work, City, Study)',
                          'channel': 'Zulu Lessons with Thando', 'minutes': 10},
                'worksheet': {
                    'instructions': 'Phendula imibuzo ngesiZulu ngemisho egcwele. (Answer the questions in isiZulu in full sentences.)',
                    'exercises': [
                        '1. Ngubani igama lakho?',
                        '2. Uneminyaka emingaki?',
                        '3. Uhlala nobani?',
                        '4. Uthanda ukwenzani ngesikhathi sakho sokuphumula?',
                        '5. Isifundo osithandayo yisiphi? Kungani?',
                        '6. Write three questions you would ask a new classmate.',
                        '7. Write a polite ending to a conversation.',
                    ],
                },
                'quiz': [
                    ('mcq', 'What does "Uthanda ukwenzani?" mean?',
                     ['Where do you live?', 'What do you like to do?', 'Who are you?', 'How old are you?'], 1),
                    ('mcq', 'How do you say "I am in Grade 9"?',
                     ['Ngifunda ibanga lesishiyagalolunye', 'Ngineminyaka eyisishiyagalolunye',
                      'Ngihlala ebangeni', 'Ngifunda izibalo'], 0),
                    ('tf', '"Kungani?" means "Why?".', True),
                    ('mcq', 'Which word means "family"?', ['isifundo', 'ingxoxo', 'umndeni', 'ibhola'], 2),
                ],
                'homework': {
                    'title': 'Oral introduction',
                    'instructions': 'Prepare a 1-minute oral in isiZulu introducing yourself fully.',
                    'tasks': [
                        'Write 6-8 sentences about your name, age, family, hobbies and favourite subject.',
                        'Practise saying it aloud without reading every word, for presentation in class.',
                    ],
                    'marks': 15,
                },
            },
            {
                'title': 'Ukufunda nokuqonda: "Usuku lokuqala" (Comprehension: "The first day")',
                'minutes': 45,
                'objectives': [
                    'I can read a short isiZulu text and identify the main idea.',
                    'I can answer literal and inferential questions about the text.',
                    'I can describe a character\'s feelings using evidence from the text.',
                ],
                'notes': (
                    '<p><strong>Umbhalo: "Usuku lokuqala"</strong></p>'
                    '<p>UThandeka ungumfundi webanga lesishiyagalolunye. Namuhla wusuku lokuqala lwesikole. '
                    'Uvuka ekuseni kakhulu, ugqoka umfaniswano wakhe, bese edla iphalishi. Usaba kancane '
                    'ngoba akazi muntu ekilasini lakhe elisha. Uthisha uyamamukela futhi umethula kubafundi. '
                    'Intombazane okuthiwa nguLindiwe ihlala eduze kwakhe. ULindiwe uthi: "Sawubona, Thandeka! '
                    'Ngiyajabula ukukwazi." Ekupheleni kosuku, uThandeka uyamamatheka. Usenomngane omusha.</p>'
                    '<p><strong>Amagama amasha (New words):</strong></p>'
                    '<ul>'
                    '<li><strong>namuhla</strong> - today; <strong>usuku lokuqala</strong> - the first day</li>'
                    '<li><strong>umfaniswano</strong> - school uniform</li>'
                    '<li><strong>usaba</strong> - she is afraid / nervous</li>'
                    '<li><strong>uyamamukela</strong> - welcomes her; <strong>umethula</strong> - introduces her</li>'
                    '<li><strong>uyamamatheka</strong> - she smiles</li>'
                    '<li><strong>usenomngane omusha</strong> - she now has a new friend</li>'
                    '</ul>'
                    '<p><strong>Types of questions:</strong> <em>literal</em> questions are answered directly '
                    'from the text; <em>inferential</em> questions ask you to think about what the text '
                    'suggests, for example how a character feels and why.</p>'
                ),
                'key_terms': [
                    ('umqondo omkhulu', 'main idea'),
                    ('umlingiswa', 'character (in a story)'),
                    ('imizwa', 'feelings'),
                    ('isihloko', 'title / topic'),
                ],
                'example': {
                    'title': 'Guided reading: literal and inferential questions',
                    'html': (
                        '<p><strong>Literal:</strong> UThandeka udlani ekuseni? <em>(What does Thandeka eat in the morning?)</em><br>'
                        '<strong>Impendulo:</strong> Udla iphalishi. <em>(She eats porridge.)</em></p>'
                        '<p><strong>Inferential:</strong> Kungani uThandeka esaba ekuqaleni? <em>(Why is Thandeka nervous at the start?)</em><br>'
                        '<strong>Impendulo:</strong> Usaba ngoba akazi muntu ekilasini elisha. <em>(She is nervous because she does not know anyone in the new class.)</em></p>'
                        '<p><strong>Feelings change:</strong> at the beginning she is nervous (<em>usaba</em>); at the end she is happy '
                        '(<em>uyamamatheka</em>) because she has a new friend. Discuss: how can you help a new learner feel welcome?</p>'
                    ),
                },
                'video': {'id': '61GPzA3O_V4', 'title': 'Ukufunda Nokuqondisisa', 'channel': 'IsiZulu with Teacher Zeey',
                          'minutes': 8},
                'worksheet': {
                    'instructions': 'Funda umbhalo "Usuku lokuqala" bese uphendula imibuzo ngemisho egcwele. (Read the text and answer in full sentences.)',
                    'exercises': [
                        '1. UThandeka ufunda ibanga lesingaki?',
                        '2. Yini uThandeka ayenzayo ekuseni? (Name two things.)',
                        '3. Kungani uThandeka esaba?',
                        '4. Ubani owethula uThandeka kubafundi?',
                        '5. Ngubani igama lentombazane ehlala eduze kukaThandeka?',
                        '6. UThandeka uzizwa kanjani ekupheleni kosuku? Kungani?',
                        '7. Give the text a different title in isiZulu.',
                    ],
                },
                'quiz': [
                    ('mcq', 'What does Thandeka eat in the morning?', ['Isinkwa', 'Iphalishi', 'Inyama', 'Ilayisi'], 1),
                    ('tf', 'Thandeka is nervous because she does not know anyone in her new class.', True),
                    ('mcq', 'What does "umfaniswano" mean?', ['Teacher', 'Friend', 'School uniform', 'Classroom'], 2),
                    ('mcq', 'How does Thandeka feel at the end of the day?',
                     ['Happy - she smiles', 'Angry', 'Tired and sad', 'Still afraid'], 0),
                ],
                'homework': {
                    'title': 'My first day',
                    'instructions': 'Write about your own first day of the school year.',
                    'tasks': [
                        'Write 6-8 isiZulu sentences about your first day: what you did in the morning, how you felt and who you met.',
                        'Underline two words that describe feelings.',
                    ],
                    'marks': 15,
                },
            },
            {
                'title': 'Izabizwana zoqobo (Absolute pronouns)',
                'minutes': 45,
                'objectives': [
                    'I can name the absolute pronouns for persons (mina, wena, yena, thina, nina, bona).',
                    'I can match absolute pronouns to noun classes.',
                    'I can use absolute pronouns for emphasis in sentences.',
                ],
                'notes': (
                    '<p>An <strong>isabizwana</strong> (pronoun) takes the place of a noun. The '
                    '<strong>absolute pronoun</strong> (<em>isabizwana soqobo</em>) is used for '
                    '<strong>emphasis</strong> or contrast, or to answer "who?" on its own.</p>'
                    '<p><strong>People (persons):</strong></p>'
                    '<ul>'
                    '<li><strong>mina</strong> - I/me &nbsp; <strong>thina</strong> - we/us</li>'
                    '<li><strong>wena</strong> - you (one) &nbsp; <strong>nina</strong> - you (many)</li>'
                    '<li><strong>yena</strong> - he/she (class 1) &nbsp; <strong>bona</strong> - they (class 2)</li>'
                    '</ul>'
                    '<p><strong>Noun classes:</strong></p>'
                    '<ul>'
                    '<li>Class 3 (umuthi) - <strong>wona</strong>; Class 4 (imithi) - <strong>yona</strong></li>'
                    '<li>Class 5 (iqanda) - <strong>lona</strong>; Class 6 (amaqanda) - <strong>wona</strong></li>'
                    '<li>Class 7 (isikole) - <strong>sona</strong>; Class 8 (izikole) - <strong>zona</strong></li>'
                    '<li>Class 9 (inja) - <strong>yona</strong>; Class 10 (izinja) - <strong>zona</strong></li>'
                    '</ul>'
                    '<p><strong>Examples:</strong></p>'
                    '<ul>'
                    '<li><strong>Mina ngithanda izibalo, kodwa wena uthanda isiNgisi.</strong> - <em>I</em> like maths, but <em>you</em> like English.</li>'
                    '<li><strong>Ubani obhale lokhu? - Yena!</strong> - Who wrote this? - <em>Him/Her!</em></li>'
                    '<li><strong>Inja yami, yona ihlala phandle.</strong> - My dog, <em>it</em> stays outside.</li>'
                    '</ul>'
                ),
                'key_terms': [
                    ('isabizwana / izabizwana', 'pronoun / pronouns'),
                    ('isabizwana soqobo', 'absolute pronoun'),
                    ('mina / wena / yena', 'I / you (one) / he or she'),
                    ('thina / nina / bona', 'we / you (many) / they'),
                ],
                'example': {
                    'title': 'Guided activity: replace and emphasise',
                    'html': (
                        '<p>Choose the correct absolute pronoun for the noun:</p>'
                        '<ul>'
                        '<li><strong>Abafundi</strong> (class 2) &rarr; <strong>bona</strong>: Abafundi, bona bayafunda. <em>(The learners, they are reading.)</em></li>'
                        '<li><strong>Isikole</strong> (class 7) &rarr; <strong>sona</strong>: Isikole, sona sikhulu. <em>(The school, it is big.)</em></li>'
                        '<li><strong>Izinja</strong> (class 10) &rarr; <strong>zona</strong>: Izinja, zona ziyakhonkotha. <em>(The dogs, they are barking.)</em></li>'
                        '</ul>'
                        '<p>Answer "Ubani?" (Who?) with an absolute pronoun: <em>Ubani ofuna ukudla? - Mina!</em> '
                        '(Who wants food? - Me!)</p>'
                    ),
                },
                'video': {'id': 'p0B_wcdy2O0',
                          'title': 'Isabizwana soqobo | Izabizwana Zoqobo | Absolute Pronouns Simplified | isiZulu FAL',
                          'channel': 'Imfundo plus', 'minutes': 8},
                'worksheet': {
                    'instructions': 'Faka isabizwana soqobo esifanele. (Fill in the correct absolute pronoun.)',
                    'exercises': [
                        '1. ___ ngiyafunda. (I)',
                        '2. ___ siyadlala ibhola. (we)',
                        '3. Umama, ___ uyapheka. (she)',
                        '4. Abangane bami, ___ bahlala eGoli. (they)',
                        '5. Isitsha, ___ sigcwele. (it - class 7)',
                        '6. Amaqanda, ___ maningi. (they - class 6)',
                        '7. Write two sentences of your own using "wena" and "nina".',
                    ],
                },
                'quiz': [
                    ('mcq', 'Which absolute pronoun means "we"?', ['nina', 'bona', 'thina', 'mina'], 2),
                    ('mcq', 'Which absolute pronoun is used for "isikole" (class 7)?',
                     ['sona', 'zona', 'lona', 'wona'], 0),
                    ('tf', '"Nina" means "you" when speaking to more than one person.', True),
                    ('mcq', 'Which absolute pronoun replaces "abafundi" (class 2)?',
                     ['yena', 'bona', 'zona', 'yona'], 1),
                ],
                'homework': {
                    'title': 'Pronoun practice',
                    'instructions': 'Complete the tasks in your exercise book.',
                    'tasks': [
                        'Write a table of the six person pronouns (mina to bona) with English meanings.',
                        'Write five sentences about your family using a different absolute pronoun in each, with translations.',
                    ],
                    'marks': 12,
                },
            },
        ],
    },
}
