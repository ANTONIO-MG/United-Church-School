"""FET Mathematics and Sciences: Term 1, Week 1 demo lessons (Grades 10-12).

Offerings (12):
    (10, 'MATH'), (11, 'MATH'), (12, 'MATH')                Mathematics
    (10, 'MLIT'), (11, 'MLIT'), (12, 'MLIT')                Mathematical Literacy
    (10, 'PHYS-SCI'), (11, 'PHYS-SCI'), (12, 'PHYS-SCI')    Physical Sciences
    (10, 'LIFE-SCI'), (11, 'LIFE-SCI'), (12, 'LIFE-SCI')    Life Sciences

Sources used for the Week 1 topics:
    * CAPS FET Mathematics Gr 10-12 (DBE, 2011): Gr 10 Algebraic expressions,
      Gr 11 Exponents and surds, Gr 12 Number patterns, sequences and series
      (first topics of the Term 1 ATP; WCED ePortal "Gr 11 Maths T1 W1 Exponents and surds").
    * CAPS FET Mathematical Literacy Gr 10-12 and the DBE 2023-2025 ATPs:
      Gr 10 Basic skills (numbers and calculations with numbers), Gr 11 Patterns,
      relationships and representations, Gr 12 Finance: financial documents
      (WCED ePortal "Gr 12 T1 W1 Mathematical Literacy: Financial documents").
    * CAPS FET Physical Sciences Gr 10-12 and DBE ATPs: Gr 10 Matter and materials
      (revise matter and classification), Gr 11 Mechanics: vectors in two dimensions,
      Gr 12 Mechanics: momentum and impulse (WCED ePortal "Physical Sciences Gr 12 T1 W1 Momentum").
    * CAPS FET Life Sciences Gr 10-12 and DBE ATPs: Gr 10 Chemistry of life (molecules
      for life), Gr 11 Biodiversity and classification of micro-organisms,
      Gr 12 DNA: the code of life.
"""

LESSONS = {
    # =====================================================================
    # MATHEMATICS
    # =====================================================================
    (10, 'MATH'): {
        'topic': 'Algebraic expressions',
        'caps': 'Functions and algebra: Algebraic expressions - the real number system '
                '(rational and irrational numbers, rounding, estimating surds), products of '
                'binomials and trinomials, factorisation (common factor, difference of two squares, '
                'trinomials, grouping, sum and difference of cubes)',
        'summary': 'We revise the real number system, then multiply out algebraic expressions '
                   '(products) and reverse the process by factorising.',
        'days': [
            {
                'title': 'The real number system',
                'minutes': 50,
                'objectives': [
                    'I can classify numbers as natural, whole, integers, rational or irrational.',
                    'I can convert a recurring decimal to a common fraction.',
                    'I can estimate a surd between two consecutive integers and round off correctly.',
                ],
                'notes': (
                    "<p>All the numbers we work with in Grade 10 are <strong>real numbers</strong> (R). "
                    "They are built up from smaller sets:</p>"
                    "<ul><li><strong>Natural numbers</strong> N = {1; 2; 3; ...}</li>"
                    "<li><strong>Whole numbers</strong> N0 = {0; 1; 2; 3; ...}</li>"
                    "<li><strong>Integers</strong> Z = {...; -2; -1; 0; 1; 2; ...}</li>"
                    "<li><strong>Rational numbers</strong> Q: any number that can be written as a/b, "
                    "where a and b are integers and b is not 0. Terminating decimals (0,75) and "
                    "recurring decimals (0,333...) are rational.</li>"
                    "<li><strong>Irrational numbers</strong> Q': numbers that cannot be written as a "
                    "fraction. Their decimals never end and never repeat, e.g. pi, √2, √7.</li></ul>"
                    "<p>Note that √9 = 3 is rational, but √10 is irrational. The value 22/7 is only an "
                    "<em>approximation</em> of pi.</p>"
                    "<p><strong>Estimating surds:</strong> find the perfect squares on either side. "
                    "Because 16 &lt; 20 &lt; 25, we know 4 &lt; √20 &lt; 5.</p>"
                    "<p><strong>Rounding off:</strong> look at the digit after the place you want. If it is "
                    "5 or more, round up; otherwise keep the digit. 3,14159 rounded to 2 decimal places is 3,14.</p>"
                ),
                'key_terms': [
                    ('rational number', 'a number that can be written as a/b with a, b integers and b not 0'),
                    ('irrational number', 'a real number that cannot be written as a fraction; non-ending, non-repeating decimal'),
                    ('surd', 'a root that cannot be simplified to a rational number, e.g. √5'),
                    ('recurring decimal', 'a decimal in which a digit or group of digits repeats forever'),
                ],
                'example': {
                    'title': 'Worked example: recurring decimal to a fraction',
                    'html': (
                        "<p>Write 0,272727... as a fraction in simplest form.</p>"
                        "<ol><li>Let x = 0,272727...</li>"
                        "<li>Two digits repeat, so multiply by 100: 100x = 27,272727...</li>"
                        "<li>Subtract: 100x - x = 27,2727... - 0,2727..., so 99x = 27</li>"
                        "<li>x = 27/99 = <strong>3/11</strong></li></ol>"
                        "<p>Check on a calculator: 3 ÷ 11 = 0,272727...</p>"
                    ),
                },
                'video': {'id': 'M8zVPUGiLM4', 'title': '1) Number Types gr 10 | Intro',
                          'channel': 'Kevinmathscience', 'minutes': 8},
                'worksheet': {
                    'instructions': 'Show all your working. Do not use a calculator for questions 1 to 4.',
                    'exercises': [
                        '1. Classify each number as rational or irrational: -5; 0,75; sqrt(9); sqrt(7); 22/7; pi',
                        '2. Write 0,444... (4 recurring) as a common fraction.',
                        '3. Write 0,151515... as a fraction in simplest form.',
                        '4. Between which two consecutive integers does sqrt(50) lie?',
                        '5. Round 3,14159 off to three decimal places.',
                        '6. Round 12 846 off to the nearest hundred.',
                        '7. Is sqrt(-4) a real number? Explain your answer.',
                    ],
                },
                'quiz': [
                    ('tf', '√16 is a rational number.', True),
                    ('mcq', 'Which of these numbers is irrational?', ['√25', '0,25', '√12', '1/3'], 2),
                    ('mcq', 'Between which two integers does √40 lie?', ['5 and 6', '6 and 7', '7 and 8', '4 and 5'], 1),
                    ('tf', '22/7 is exactly equal to pi.', False),
                    ('mcq', 'Write 0,555... (5 recurring) as a fraction.', ['5/10', '5/9', '1/2', '5/99'], 1),
                ],
                'homework': {
                    'title': 'Number system practice',
                    'instructions': 'Complete the tasks in your exercise book. Show your working.',
                    'tasks': [
                        'Write 0,363636... as a fraction in simplest form.',
                        'Estimate sqrt(75) between two consecutive integers and explain how you decided.',
                        'Give one example each of a natural number, a negative integer, a rational non-integer and an irrational number.',
                    ],
                    'marks': 10,
                },
            },
            {
                'title': 'Products of algebraic expressions',
                'minutes': 50,
                'objectives': [
                    'I can multiply a binomial by a binomial.',
                    'I can square a binomial and recognise the difference of two squares.',
                    'I can multiply a binomial by a trinomial and simplify.',
                ],
                'notes': (
                    "<p>To find a <strong>product</strong> we multiply every term in the first bracket by "
                    "every term in the second bracket (the distributive law), then collect like terms.</p>"
                    "<p><strong>Binomial x binomial:</strong> (a + b)(c + d) = ac + ad + bc + bd. "
                    "Some learners remember this as FOIL: First, Outer, Inner, Last.</p>"
                    "<p><strong>Special products</strong> worth knowing:</p>"
                    "<ul><li>(a + b)² = a² + 2ab + b²</li>"
                    "<li>(a - b)² = a² - 2ab + b²</li>"
                    "<li>(a + b)(a - b) = a² - b² (the difference of two squares)</li></ul>"
                    "<p>A common error is to write (x + 3)² = x² + 9. This is wrong: (x + 3)² = (x + 3)(x + 3) "
                    "= x² + 6x + 9.</p>"
                    "<p><strong>Binomial x trinomial:</strong> multiply each of the two terms in the binomial by "
                    "all three terms in the trinomial, giving six terms, then simplify. A useful result is "
                    "(a + b)(a² - ab + b²) = a³ + b³.</p>"
                    "<p>Always arrange your final answer in descending powers of the variable.</p>"
                ),
                'key_terms': [
                    ('binomial', 'an expression with two terms, e.g. 2x + 3'),
                    ('trinomial', 'an expression with three terms, e.g. x² - 3x + 4'),
                    ('like terms', 'terms with the same variables raised to the same powers'),
                    ('product', 'the result of multiplying expressions'),
                ],
                'example': {
                    'title': 'Worked examples: expanding brackets',
                    'html': (
                        "<p><strong>(a)</strong> (2x + 3)(x - 5) = 2x² - 10x + 3x - 15 = <strong>2x² - 7x - 15</strong></p>"
                        "<p><strong>(b)</strong> (3x - 2)² = 9x² - 6x - 6x + 4 = <strong>9x² - 12x + 4</strong></p>"
                        "<p><strong>(c)</strong> (x + 2)(x² - 3x + 4)<br>"
                        "= x³ - 3x² + 4x + 2x² - 6x + 8<br>"
                        "= <strong>x³ - x² - 2x + 8</strong></p>"
                    ),
                },
                'video': {'id': 'tVf5ek8E5d0',
                          'title': 'Binomial x Binomial Grade 10 Maths Products | Simplifying Algebraic Expressions',
                          'channel': 'Miss Martins Maths and Science', 'minutes': 12},
                'worksheet': {
                    'instructions': 'Expand and simplify each expression.',
                    'exercises': [
                        '1. (x + 4)(x + 7)',
                        '2. (2a - 3)(a + 5)',
                        '3. (x - 6)(x + 6)',
                        '4. (4y + 1)²',
                        '5. (3m - 2n)²',
                        '6. (x - 1)(x² + x + 1)',
                        '7. (2x + 3)(x² - 4x + 2)',
                        '8. 2(x + 3)² - (x - 1)(x + 1)',
                    ],
                },
                'quiz': [
                    ('mcq', 'Expand (x + 4)(x - 4).', ['x² + 16', 'x² - 8x - 16', 'x² - 16', 'x² + 8x + 16'], 2),
                    ('mcq', 'Expand (2a - 1)².', ['4a² - 1', '4a² - 4a + 1', '4a² + 1', '4a² - 2a + 1'], 1),
                    ('tf', '(x + 3)² = x² + 9', False),
                    ('mcq', 'What is the coefficient of x in (x + 5)(x - 2)?', ['3', '-3', '7', '-10'], 0),
                ],
                'homework': {
                    'title': 'Products practice',
                    'instructions': 'Expand and simplify. Show every step.',
                    'tasks': [
                        '(3x - 4)(2x + 1)',
                        '(5 - 2y)²',
                        '(a + 3)(a² - 3a + 9)',
                        '(x + 2)² - (x - 2)²',
                    ],
                    'marks': 12,
                },
            },
            {
                'title': 'Factorisation',
                'minutes': 55,
                'objectives': [
                    'I can take out the highest common factor.',
                    'I can factorise the difference of two squares and trinomials.',
                    'I can factorise by grouping and factorise the sum or difference of two cubes.',
                ],
                'notes': (
                    "<p><strong>Factorisation</strong> is the reverse of finding a product: we write an expression "
                    "as a product of factors. Follow this order:</p>"
                    "<ol><li><strong>Common factor first.</strong> Take out the highest common factor (HCF): "
                    "6x² - 9x = 3x(2x - 3).</li>"
                    "<li><strong>Two terms?</strong> Check for the difference of two squares: a² - b² = (a - b)(a + b). "
                    "A sum of two squares such as x² + 4 cannot be factorised. Check for cubes: "
                    "a³ + b³ = (a + b)(a² - ab + b²) and a³ - b³ = (a - b)(a² + ab + b²).</li>"
                    "<li><strong>Three terms?</strong> Factorise the trinomial ax² + bx + c. Find two numbers whose "
                    "product is a x c and whose sum is b.</li>"
                    "<li><strong>Four terms?</strong> Try grouping in pairs: ax + ay + bx + by = a(x + y) + b(x + y) "
                    "= (x + y)(a + b).</li></ol>"
                    "<p>Always check whether a factor can be factorised further, and check your answer by "
                    "multiplying it out again.</p>"
                ),
                'key_terms': [
                    ('factor', 'an expression that divides exactly into another expression'),
                    ('HCF', 'highest common factor: the biggest factor shared by all the terms'),
                    ('difference of two squares', 'an expression of the form a² - b², which factorises to (a - b)(a + b)'),
                ],
                'example': {
                    'title': 'Worked examples: factorising',
                    'html': (
                        "<p><strong>(a)</strong> 4x² - 25 = (2x)² - 5² = <strong>(2x - 5)(2x + 5)</strong></p>"
                        "<p><strong>(b)</strong> x² - x - 12: we need two numbers with product -12 and sum -1, "
                        "namely -4 and 3. So x² - x - 12 = <strong>(x - 4)(x + 3)</strong>.</p>"
                        "<p><strong>(c)</strong> 2x² + 7x + 3: a x c = 6; the numbers 6 and 1 have sum 7.<br>"
                        "2x² + 6x + x + 3 = 2x(x + 3) + 1(x + 3) = <strong>(x + 3)(2x + 1)</strong></p>"
                        "<p><strong>(d)</strong> x³ - 8 = <strong>(x - 2)(x² + 2x + 4)</strong></p>"
                    ),
                },
                'video': {'id': 'L1ZeoZyh69s',
                          'title': 'Factorising Grade 10 Maths Difference of Two Squares (DOTS)',
                          'channel': 'Miss Martins Maths and Science', 'minutes': 10},
                'worksheet': {
                    'instructions': 'Factorise fully. Check each answer by multiplying out.',
                    'exercises': [
                        '1. 5a²b - 10ab²',
                        '2. 9y² - 1',
                        '3. x² + 5x + 6',
                        '4. 3x² - 12',
                        '5. 2x² - 5x - 3',
                        '6. xy - 3x + 2y - 6',
                        '7. a³ + 27',
                        '8. x^4 - 16',
                    ],
                },
                'quiz': [
                    ('mcq', 'Factorise x² - 9.', ['(x - 3)²', '(x - 3)(x + 3)', '(x - 9)(x + 1)', 'x(x - 9)'], 1),
                    ('mcq', 'Factorise x² + 2x - 15.', ['(x + 5)(x - 3)', '(x - 5)(x + 3)', '(x + 15)(x - 1)', '(x + 3)(x + 5)'], 0),
                    ('tf', 'x² + 4 can be factorised as (x + 2)(x - 2).', False),
                    ('mcq', 'What is the HCF of 8x³ and 12x²?', ['4x', '24x³', '2x²', '4x²'], 3),
                    ('mcq', 'Factorise a³ + 27.', ['(a + 3)³', '(a - 3)(a² + 3a + 9)', '(a + 3)(a² - 3a + 9)', '(a + 3)(a² + 9)'], 2),
                ],
                'homework': {
                    'title': 'Factorisation practice',
                    'instructions': 'Factorise each expression fully and show your method.',
                    'tasks': [
                        '12x²y - 18xy²',
                        '16 - 49m²',
                        '3x² + 10x - 8',
                        '2ax - 4a + 3x - 6',
                    ],
                    'marks': 12,
                },
            },
        ],
    },

    (11, 'MATH'): {
        'topic': 'Exponents and surds',
        'caps': 'Functions and algebra: Exponents and surds - simplify expressions and solve equations '
                'using the laws of exponents for rational exponents (x^(p/q) is the q-th root of x^p); '
                'add, subtract, multiply and divide simple surds; solve simple equations involving surds',
        'summary': 'We extend the laws of exponents to rational exponents, simplify surds and solve '
                   'exponential and surd equations.',
        'days': [
            {
                'title': 'Laws of exponents and rational exponents',
                'minutes': 50,
                'objectives': [
                    'I can apply the laws of exponents, including zero and negative exponents.',
                    'I can evaluate expressions with rational exponents such as 8^(2/3).',
                    'I can simplify expressions by writing numbers as powers of prime bases.',
                ],
                'notes': (
                    "<p>Revise the laws of exponents (a, b not 0; m, n rational):</p>"
                    "<ul><li>a^m x a^n = a^(m + n)</li>"
                    "<li>a^m ÷ a^n = a^(m - n)</li>"
                    "<li>(a^m)^n = a^(mn) and (ab)^n = a^n b^n</li>"
                    "<li>a^0 = 1 and a^(-n) = 1/a^n</li></ul>"
                    "<p><strong>Rational exponents:</strong> a^(m/n) means the n-th root of a^m. The denominator "
                    "of the exponent gives the root and the numerator gives the power. It is usually easiest "
                    "to take the root first: 8^(2/3) = (cube root of 8)² = 2² = 4.</p>"
                    "<p><strong>Prime bases:</strong> when bases are different, write each base as a product of "
                    "primes (4 = 2², 9 = 3², 27 = 3³, 81 = 3^4) and then use the laws.</p>"
                    "<p><strong>Factorising:</strong> if there is a plus or minus sign between powers, you cannot "
                    "simply add exponents. Take out a common factor first, e.g. 2^(x+2) - 2^x = 2^x(2² - 1) = 3 x 2^x.</p>"
                ),
                'key_terms': [
                    ('base', 'the number being multiplied repeatedly, e.g. 2 in 2^5'),
                    ('exponent', 'the power that tells how many times the base is used as a factor'),
                    ('rational exponent', 'an exponent written as a fraction m/n, meaning the n-th root of the m-th power'),
                ],
                'example': {
                    'title': 'Worked examples: simplifying with exponents',
                    'html': (
                        "<p><strong>(a)</strong> 27^(-1/3) = 1 / 27^(1/3) = <strong>1/3</strong></p>"
                        "<p><strong>(b)</strong> (9^x x 27^(x+1)) / 81^x = (3^(2x) x 3^(3x+3)) / 3^(4x) "
                        "= 3^(2x + 3x + 3 - 4x) = <strong>3^(x+3)</strong></p>"
                        "<p><strong>(c)</strong> (2^(x+2) - 2^x) / (3 x 2^x) = 2^x(4 - 1) / (3 x 2^x) = <strong>1</strong></p>"
                    ),
                },
                'video': {'id': 'EL1z_5pWAbk',
                          'title': 'Grade 11 Exponents | Grade 10 Exponent law and basic examples REVISION',
                          'channel': 'Miss Martins Maths and Science', 'minutes': 15},
                'worksheet': {
                    'instructions': 'Simplify without a calculator. Leave answers with positive exponents.',
                    'exercises': [
                        '1. 16^(3/4)',
                        '2. 32^(-2/5)',
                        '3. (2x³)^4 ÷ 8x^5',
                        '4. (4^x x 8^(x-1)) / 2^(5x)',
                        '5. (3^(x+1) + 3^x) / (4 x 3^x)',
                        '6. (a^(1/2) x a^(3/2))^2',
                        '7. (125x^6)^(1/3)',
                    ],
                },
                'quiz': [
                    ('mcq', 'Evaluate 16^(3/4).', ['12', '8', '6', '64'], 1),
                    ('mcq', 'Evaluate 25^(-1/2).', ['-5', '5', '-1/5', '1/5'], 3),
                    ('tf', '(x³)² = x^5', False),
                    ('mcq', 'Simplify 2^x x 4^x.', ['6^x', '2^(2x)', '8^x', '16^x'], 2),
                    ('tf', 'a^0 = 1 for every real number a that is not 0.', True),
                ],
                'homework': {
                    'title': 'Exponent laws practice',
                    'instructions': 'Simplify each expression. Show all steps.',
                    'tasks': [
                        '81^(-3/4)',
                        '(6^x x 9^(x+1)) / (2^x x 27^(x+1))',
                        '(5^(x+2) - 5^x) / (24 x 5^x)',
                    ],
                    'marks': 10,
                },
            },
            {
                'title': 'Simplifying surds',
                'minutes': 50,
                'objectives': [
                    'I can simplify a surd by taking out perfect square factors.',
                    'I can add and subtract like surds.',
                    'I can multiply and divide surds, including expanding brackets.',
                ],
                'notes': (
                    "<p>A <strong>surd</strong> is a root of a number that is irrational, such as √2 or √50. "
                    "Surds can also be written with rational exponents: √a = a^(1/2).</p>"
                    "<p><strong>Rules</strong> (for a, b &gt;= 0):</p>"
                    "<ul><li>√a x √b = √(ab)</li>"
                    "<li>√a ÷ √b = √(a/b), b not 0</li>"
                    "<li>√a x √a = a</li></ul>"
                    "<p><strong>Simplifying:</strong> write the number as a product with the largest perfect square: "
                    "√50 = √(25 x 2) = 5√2.</p>"
                    "<p><strong>Adding and subtracting:</strong> only <em>like surds</em> (the same number under "
                    "the root) can be added: 3√2 + 5√2 = 8√2. Unlike surds may become like surds after "
                    "simplifying: √12 + √27 = 2√3 + 3√3 = 5√3.</p>"
                    "<p>Be careful: √9 + √16 = 3 + 4 = 7, which is NOT equal to √25 = 5. You cannot add the "
                    "numbers under the roots.</p>"
                    "<p><strong>Brackets:</strong> expand as in algebra. (√3 + 2)(√3 - 2) = 3 - 4 = -1, a difference "
                    "of two squares.</p>"
                ),
                'key_terms': [
                    ('surd', 'an irrational root, e.g. √3'),
                    ('like surds', 'surds with the same number under the same root sign'),
                    ('perfect square', 'a number that is the square of an integer: 1, 4, 9, 16, 25, ...'),
                ],
                'example': {
                    'title': 'Worked examples: surds',
                    'html': (
                        "<p><strong>(a)</strong> √48 - √75 + √3 = 4√3 - 5√3 + √3 = <strong>0</strong></p>"
                        "<p><strong>(b)</strong> (2 + √5)² = 4 + 4√5 + 5 = <strong>9 + 4√5</strong></p>"
                        "<p><strong>(c)</strong> √18 x √8 = √144 = <strong>12</strong></p>"
                        "<p><strong>(d)</strong> √72 / √2 = √36 = <strong>6</strong></p>"
                    ),
                },
                'video': {'id': 'BXvpE1hv4XM', 'title': '2) Simplify surds grade 11',
                          'channel': 'Kevinmathscience', 'minutes': 8},
                'worksheet': {
                    'instructions': 'Simplify without a calculator. Write sqrt(a) for the square root of a.',
                    'exercises': [
                        '1. sqrt(98)',
                        '2. sqrt(20) + sqrt(45)',
                        '3. 3sqrt(8) - sqrt(50)',
                        '4. sqrt(6) x sqrt(15)',
                        '5. (sqrt(7) - 2)(sqrt(7) + 2)',
                        '6. (3 - sqrt(2))²',
                        '7. sqrt(200) / sqrt(8)',
                    ],
                },
                'quiz': [
                    ('mcq', 'Simplify √72.', ['4√2', '8√3', '6√2', '36√2'], 2),
                    ('mcq', 'Simplify √18 + √8.', ['√26', '5√2', '26', '2√5'], 1),
                    ('tf', '√9 + √16 = √25', False),
                    ('mcq', 'Simplify (√5 - 1)(√5 + 1).', ['6', '24', '4', '√5'], 2),
                ],
                'homework': {
                    'title': 'Surds practice',
                    'instructions': 'Simplify each expression fully.',
                    'tasks': [
                        'sqrt(27) + sqrt(12) - sqrt(3)',
                        '(2sqrt(3) + 1)²',
                        'sqrt(10) x sqrt(40)',
                        'Show that (sqrt(5) + sqrt(3))(sqrt(5) - sqrt(3)) is a rational number.',
                    ],
                    'marks': 12,
                },
            },
            {
                'title': 'Exponential and surd equations',
                'minutes': 55,
                'objectives': [
                    'I can solve exponential equations by writing both sides with the same base.',
                    'I can solve exponential equations by factorising a common power.',
                    'I can solve equations with surds and check for invalid solutions.',
                ],
                'notes': (
                    "<p><strong>Exponential equations</strong> have the unknown in the exponent, e.g. 2^x = 32.</p>"
                    "<p><strong>Method 1: same base.</strong> If a^x = a^y (a &gt; 0, a not 1) then x = y. "
                    "Write 32 = 2^5, so x = 5. Remember 1/9 = 3^(-2) and 1 = a^0.</p>"
                    "<p><strong>Method 2: factorise.</strong> If there are terms added or subtracted, take out the "
                    "common power, e.g. 2^(x+1) + 2^x = 2^x(2 + 1).</p>"
                    "<p><strong>Rational exponents:</strong> to solve x^(3/2) = 8, raise both sides to the reciprocal "
                    "power: x = 8^(2/3) = 4.</p>"
                    "<p><strong>Surd equations</strong> have the unknown under a root. Steps:</p>"
                    "<ol><li>Isolate the root on one side.</li>"
                    "<li>Square both sides.</li>"
                    "<li>Solve the resulting (often quadratic) equation.</li>"
                    "<li><strong>Check every answer in the original equation.</strong> Squaring can create "
                    "extra solutions that do not work, because a square root is never negative.</li></ol>"
                ),
                'key_terms': [
                    ('exponential equation', 'an equation in which the unknown is in the exponent'),
                    ('extraneous solution', 'an answer that comes out of the working but does not satisfy the original equation'),
                ],
                'example': {
                    'title': 'Worked examples: solving equations',
                    'html': (
                        "<p><strong>(a)</strong> 3^(x+1) = 1/9<br>3^(x+1) = 3^(-2), so x + 1 = -2 and <strong>x = -3</strong>.</p>"
                        "<p><strong>(b)</strong> 2^(x+1) + 2^x = 24<br>2^x(2 + 1) = 24, so 2^x = 8 = 2³ and <strong>x = 3</strong>.</p>"
                        "<p><strong>(c)</strong> √(x + 3) = x - 3<br>Square: x + 3 = x² - 6x + 9<br>"
                        "x² - 7x + 6 = 0, so (x - 6)(x - 1) = 0 and x = 6 or x = 1.<br>"
                        "Check x = 6: √9 = 3 and 6 - 3 = 3. Valid.<br>"
                        "Check x = 1: √4 = 2 but 1 - 3 = -2. Not valid.<br>"
                        "So <strong>x = 6</strong> only.</p>"
                    ),
                },
                'video': {'id': '2Wo5c9MCoJE', 'title': 'Exponential Equations Grade 11 Exponents and Equations',
                          'channel': 'Miss Martins Maths and Science', 'minutes': 15},
                'worksheet': {
                    'instructions': 'Solve for x. Check answers to surd equations.',
                    'exercises': [
                        '1. 5^x = 125',
                        '2. 2^(x-1) = 1/8',
                        '3. 9^x = 27',
                        '4. 3^(x+2) - 3^x = 72',
                        '5. x^(3/2) = 27',
                        '6. sqrt(x + 7) = x + 1',
                        '7. sqrt(2x - 1) - 3 = 0',
                    ],
                },
                'quiz': [
                    ('mcq', 'Solve 5^x = 125.', ['x = 25', 'x = 3', 'x = 5', 'x = 1/3'], 1),
                    ('mcq', 'Solve 2^(x-1) = 1/8.', ['x = -4', 'x = -3', 'x = -2', 'x = 4'], 2),
                    ('tf', 'When you square both sides of a surd equation, you must check your answers in the original equation.', True),
                    ('mcq', 'Solve 3^x x 3 = 81.', ['x = 27', 'x = 4', 'x = 26', 'x = 3'], 3),
                ],
                'homework': {
                    'title': 'Equations with exponents and surds',
                    'instructions': 'Solve each equation and show all working.',
                    'tasks': [
                        '4^(x+1) = 32',
                        '2^(x+2) + 2^x = 40',
                        'sqrt(x + 1) = x - 5',
                    ],
                    'marks': 12,
                },
            },
        ],
    },

    (12, 'MATH'): {
        'topic': 'Number patterns, sequences and series',
        'caps': 'Number patterns, sequences and series: arithmetic and geometric sequences, '
                'the general term, sigma notation, derivation and application of the formulae for '
                'the sum of arithmetic and geometric series',
        'summary': 'We find general terms of arithmetic and geometric sequences, then use sigma '
                   'notation and the arithmetic series formula.',
        'days': [
            {
                'title': 'Arithmetic sequences',
                'minutes': 50,
                'objectives': [
                    'I can identify an arithmetic sequence and its common difference.',
                    'I can find and use the general term Tn = a + (n - 1)d.',
                    'I can find which term of a sequence has a given value.',
                ],
                'notes': (
                    "<p>An <strong>arithmetic sequence</strong> has a constant difference between consecutive terms. "
                    "This is the <strong>common difference</strong> d = T2 - T1 = T3 - T2.</p>"
                    "<p>If the first term is a, the terms are a; a + d; a + 2d; ... so the general term is</p>"
                    "<p><strong>Tn = a + (n - 1)d</strong></p>"
                    "<p>where n is the position of the term (n = 1; 2; 3; ...). n must be a natural number, so if "
                    "solving for n gives a fraction, the value is not a term of the sequence.</p>"
                    "<p>An arithmetic sequence is a <em>linear</em> pattern: its graph is a set of points on a "
                    "straight line with gradient d.</p>"
                    "<p><strong>Revision: quadratic patterns.</strong> If the first differences are not constant but "
                    "the second differences are, the pattern is quadratic: Tn = an² + bn + c, where "
                    "2a = second difference, 3a + b = T2 - T1 and a + b + c = T1.</p>"
                    "<p>To show three terms are arithmetic, show T2 - T1 = T3 - T2.</p>"
                ),
                'key_terms': [
                    ('sequence', 'an ordered list of numbers following a rule'),
                    ('common difference (d)', 'the constant amount added to get from one term to the next'),
                    ('general term (Tn)', 'a formula that gives any term from its position n'),
                ],
                'example': {
                    'title': 'Worked example: 5; 9; 13; ...',
                    'html': (
                        "<p>a = 5 and d = 9 - 5 = 4.</p>"
                        "<p><strong>General term:</strong> Tn = 5 + (n - 1)(4) = <strong>4n + 1</strong></p>"
                        "<p><strong>T20</strong> = 4(20) + 1 = <strong>81</strong></p>"
                        "<p><strong>Which term is 201?</strong> 4n + 1 = 201, so 4n = 200 and <strong>n = 50</strong>. "
                        "201 is the 50th term.</p>"
                        "<p><strong>Is 100 a term?</strong> 4n + 1 = 100 gives n = 24,75, not a natural number, so no.</p>"
                    ),
                },
                'video': {'id': 'S9oGEqRqO_8',
                          'title': 'Grade 12 Algebra Lesson 1| Sequences and Series : Arithmetic Sequence Explained',
                          'channel': 'Mlungisi Nkosi Maths & Science', 'minutes': 15},
                'worksheet': {
                    'instructions': 'Show all working.',
                    'exercises': [
                        '1. Find d and T15 for 3; 10; 17; ...',
                        '2. Find the general term of 20; 17; 14; ...',
                        '3. Which term of 7; 12; 17; ... is equal to 252?',
                        '4. Is 150 a term of 2; 6; 10; ...? Explain.',
                        '5. Find x if x - 1; 2x + 1; 4x - 1 form an arithmetic sequence.',
                        '6. In an arithmetic sequence T3 = 11 and T8 = 31. Find a and d.',
                        '7. Find Tn for the quadratic pattern 3; 8; 15; 24; ...',
                    ],
                },
                'quiz': [
                    ('mcq', 'What is the common difference of 7; 4; 1; -2; ...?', ['3', '-3', '-2', '4'], 1),
                    ('mcq', 'Find T10 of 2; 5; 8; ...', ['30', '32', '29', '27'], 2),
                    ('tf', '1; 4; 9; 16; ... is an arithmetic sequence.', False),
                    ('mcq', 'Which is the general term of 3; 7; 11; ...?', ['4n + 3', '4n - 1', '3n + 4', 'n + 4'], 1),
                ],
                'homework': {
                    'title': 'Arithmetic sequences',
                    'instructions': 'Answer in your exercise book.',
                    'tasks': [
                        'Find the 25th term of 11; 8; 5; ...',
                        'Which term of 4; 11; 18; ... is 361?',
                        'The 5th term of an arithmetic sequence is 23 and the 12th term is 58. Find the first term and the common difference.',
                    ],
                    'marks': 12,
                },
            },
            {
                'title': 'Geometric sequences',
                'minutes': 50,
                'objectives': [
                    'I can identify a geometric sequence and find its constant ratio.',
                    'I can find and use the general term Tn = ar^(n-1).',
                    'I can solve problems involving geometric sequences, including finding n.',
                ],
                'notes': (
                    "<p>A <strong>geometric sequence</strong> has a constant <strong>ratio</strong> between consecutive "
                    "terms: each term is multiplied by the same number r to get the next one.</p>"
                    "<p>r = T2 / T1 = T3 / T2</p>"
                    "<p>The terms are a; ar; ar²; ar³; ... so the general term is</p>"
                    "<p><strong>Tn = a r^(n-1)</strong></p>"
                    "<p>Points to remember:</p>"
                    "<ul><li>If r &gt; 1 the terms grow quickly (exponential growth).</li>"
                    "<li>If 0 &lt; r &lt; 1 the terms get smaller and approach 0.</li>"
                    "<li>If r &lt; 0 the terms alternate between positive and negative.</li>"
                    "<li>r cannot be 0, and no term can be 0.</li></ul>"
                    "<p>To find n, make the power the subject and write both sides with the same base "
                    "(or use logarithms, which you will meet later in Grade 12).</p>"
                    "<p>To show three terms are geometric, show T2/T1 = T3/T2.</p>"
                ),
                'key_terms': [
                    ('geometric sequence', 'a sequence with a constant ratio between consecutive terms'),
                    ('constant ratio (r)', 'the number each term is multiplied by to get the next term'),
                ],
                'example': {
                    'title': 'Worked examples: geometric sequences',
                    'html': (
                        "<p><strong>(a)</strong> 3; 6; 12; ...: a = 3, r = 2, Tn = 3(2)^(n-1).<br>"
                        "T8 = 3(2)^7 = 3 x 128 = <strong>384</strong>.</p>"
                        "<p><strong>Which term is 1 536?</strong> 3(2)^(n-1) = 1 536, so 2^(n-1) = 512 = 2^9.<br>"
                        "n - 1 = 9 and <strong>n = 10</strong>.</p>"
                        "<p><strong>(b)</strong> 64; -32; 16; ...: r = -32/64 = -1/2.<br>"
                        "T7 = 64(-1/2)^6 = 64/64 = <strong>1</strong>.</p>"
                        "<p><strong>(c)</strong> 2; x; 18 is geometric: x/2 = 18/x, so x² = 36 and <strong>x = 6 or x = -6</strong>.</p>"
                    ),
                },
                'video': {'id': 'ZSxq7Ay48NQ', 'title': '4)Gr 12 Geometric Sequence | Intro',
                          'channel': 'Kevinmathscience', 'minutes': 8},
                'worksheet': {
                    'instructions': 'Show all working.',
                    'exercises': [
                        '1. Find r and T6 for 5; 15; 45; ...',
                        '2. Find the general term of 48; 24; 12; ...',
                        '3. Find T9 of 1; -2; 4; -8; ...',
                        '4. Which term of 2; 6; 18; ... is 1 458?',
                        '5. Find k if k - 2; k + 1; 3k + 3 is a geometric sequence (k > 0).',
                        '6. In a geometric sequence T2 = 12 and T5 = 96. Find a and r.',
                    ],
                },
                'quiz': [
                    ('mcq', 'What is the constant ratio of 81; 27; 9; ...?', ['3', '1/3', '-3', '9'], 1),
                    ('mcq', 'Find T6 of 2; 6; 18; ...', ['162', '1 458', '243', '486'], 3),
                    ('tf', '5; -10; 20; -40; ... is a geometric sequence with r = -2.', True),
                    ('mcq', 'Which is the general term of 1; 4; 16; ...?', ['4^n', '4^(n-1)', '4n - 3', 'n²'], 1),
                ],
                'homework': {
                    'title': 'Geometric sequences',
                    'instructions': 'Answer in your exercise book.',
                    'tasks': [
                        'Find the 7th term of 729; 243; 81; ...',
                        'Which term of 3; 12; 48; ... is 3 072?',
                        'A ball is dropped from 8 m and each bounce reaches 3/4 of the previous height. Find the height of the 4th bounce.',
                    ],
                    'marks': 10,
                },
            },
            {
                'title': 'Sigma notation and arithmetic series',
                'minutes': 55,
                'objectives': [
                    'I can read, write and expand sigma notation.',
                    'I can find the number of terms in a sum written in sigma notation.',
                    'I can use Sn = n/2[2a + (n - 1)d] to find the sum of an arithmetic series.',
                ],
                'notes': (
                    "<p>A <strong>series</strong> is the sum of the terms of a sequence. Sn means the sum of the first n terms.</p>"
                    "<p><strong>Sigma notation</strong> uses the Greek capital letter Σ (sigma) to mean 'the sum of'. "
                    "For example Σ (from k = 1 to 5) of (2k + 1) means substitute k = 1; 2; 3; 4; 5 and add: "
                    "3 + 5 + 7 + 9 + 11 = 35.</p>"
                    "<p><strong>Number of terms</strong> = top value - bottom value + 1. Σ from k = 3 to 12 has 12 - 3 + 1 = 10 terms.</p>"
                    "<p><strong>Arithmetic series formula.</strong> Write the sum forwards and backwards and add: each pair "
                    "adds to (a + l), and there are n pairs, so 2Sn = n(a + l). This gives</p>"
                    "<ul><li><strong>Sn = n/2 (a + l)</strong>, where l is the last term, or</li>"
                    "<li><strong>Sn = n/2 [2a + (n - 1)d]</strong></li></ul>"
                    "<p>The young Carl Gauss is said to have used this idea to add 1 + 2 + ... + 100 = 50 x 101 = 5 050.</p>"
                    "<p>Next week we derive the formula for geometric series.</p>"
                ),
                'key_terms': [
                    ('series', 'the sum of the terms of a sequence'),
                    ('sigma notation', 'a short way to write a sum using the symbol Σ'),
                    ('Sn', 'the sum of the first n terms'),
                ],
                'example': {
                    'title': 'Worked examples: arithmetic series',
                    'html': (
                        "<p><strong>(a)</strong> Find the sum of the first 20 terms of 4 + 7 + 10 + ...<br>"
                        "a = 4, d = 3, n = 20<br>"
                        "S20 = 20/2 [2(4) + 19(3)] = 10[8 + 57] = <strong>650</strong></p>"
                        "<p><strong>(b)</strong> Evaluate Σ (k = 1 to 30) of (3k - 1).<br>"
                        "First term (k = 1): 2. Last term (k = 30): 89. Number of terms: 30.<br>"
                        "S30 = 30/2 (2 + 89) = 15 x 91 = <strong>1 365</strong></p>"
                    ),
                },
                'video': {'id': 'nLEER8FFzHg', 'title': '14) Sigma Grade 12 | Intro',
                          'channel': 'Kevinmathscience', 'minutes': 8},
                'worksheet': {
                    'instructions': 'In this worksheet "sum(k=1 to 5) of (2k+1)" means sigma notation.',
                    'exercises': [
                        '1. Expand and evaluate sum(k=1 to 6) of (4k - 3).',
                        '2. How many terms are there in sum(k=5 to 40) of (2k)?',
                        '3. Write 2 + 5 + 8 + ... + 59 in sigma notation.',
                        '4. Find the sum of the first 25 terms of 6 + 10 + 14 + ...',
                        '5. Evaluate sum(n=1 to 50) of (2n + 3).',
                        '6. How many terms of 3 + 7 + 11 + ... must be added to give 210?',
                    ],
                },
                'quiz': [
                    ('mcq', 'How many terms are there in Σ from k = 3 to 12?', ['9', '10', '12', '11'], 1),
                    ('mcq', 'Evaluate Σ from k = 1 to 4 of k².', ['10', '16', '30', '20'], 2),
                    ('tf', '1 + 2 + 3 + ... + 100 = 5 050', True),
                    ('mcq', 'Find S10 for 2 + 5 + 8 + ...', ['145', '155', '165', '310'], 1),
                ],
                'homework': {
                    'title': 'Series and sigma notation',
                    'instructions': 'Show all working.',
                    'tasks': [
                        'Evaluate sum(k=1 to 20) of (5k - 2).',
                        'Find the sum of all the multiples of 3 between 1 and 100.',
                        'Write 10 + 7 + 4 + ... + (-50) in sigma notation and calculate its value.',
                    ],
                    'marks': 12,
                },
            },
        ],
    },

    # =====================================================================
    # MATHEMATICAL LITERACY
    # =====================================================================
    (10, 'MLIT'): {
        'topic': 'Basic skills: numbers and calculations with numbers',
        'caps': 'Basic skills topics: Interpreting and communicating answers and calculations; '
                'Numbers and calculations with numbers - number formats and conventions, operations, '
                'rounding, ratio, proportion, rate and percentages',
        'summary': 'We practise working with numbers in everyday contexts: number formats, '
                   'operations and rounding, ratio and rate, and percentages.',
        'days': [
            {
                'title': 'Number formats, operations and rounding',
                'minutes': 45,
                'objectives': [
                    'I can read and write numbers in different formats, including large numbers and money.',
                    'I can use the correct order of operations, with and without a calculator.',
                    'I can round off correctly and decide when to round up or down in context.',
                ],
                'notes': (
                    "<p>Mathematical Literacy is about using numbers to make sense of real life. In South Africa we "
                    "use a <strong>decimal comma</strong> (R12,50) and a <strong>space</strong> to group thousands "
                    "(R1 250 000). Large numbers are often written in words: R2,5 million = R2 500 000.</p>"
                    "<p><strong>Order of operations (BODMAS):</strong> Brackets, Of (powers and roots), Division and "
                    "Multiplication (left to right), Addition and Subtraction (left to right). "
                    "So 4 + 6 x 2 = 4 + 12 = 16, not 20.</p>"
                    "<p><strong>Rounding:</strong> in normal rounding, 5 and above rounds up. Money is usually rounded "
                    "to 2 decimal places (cents). But the <em>context</em> matters:</p>"
                    "<ul><li><strong>Round up</strong> when you need enough: if you need 4,2 tins of paint, you must buy 5 tins.</li>"
                    "<li><strong>Round down</strong> when you can only use complete items: with R100 and cooldrinks at "
                    "R15 each you can buy 6 (100 ÷ 15 = 6,67), not 7.</li></ul>"
                    "<p>Always write the answer to a word problem as a sentence with the correct unit, and check "
                    "whether the answer makes sense.</p>"
                ),
                'key_terms': [
                    ('BODMAS', 'the order of operations: Brackets, Of, Division, Multiplication, Addition, Subtraction'),
                    ('rounding', 'replacing a number with a simpler value close to it'),
                    ('estimate', 'a quick, approximate answer used to check a calculation'),
                ],
                'example': {
                    'title': 'Worked example: a shopping trip',
                    'html': (
                        "<p>Thandi buys 3 loaves of bread at R18,50 each and 2 bottles of milk at R27,99 each. "
                        "She pays with R150. How much change does she get?</p>"
                        "<ol><li>Bread: 3 x R18,50 = R55,50</li>"
                        "<li>Milk: 2 x R27,99 = R55,98</li>"
                        "<li>Total: R55,50 + R55,98 = R111,48</li>"
                        "<li>Change: R150,00 - R111,48 = <strong>R38,52</strong></li></ol>"
                        "<p><strong>Estimate to check:</strong> 3 x R20 + 2 x R30 = R120, so the total of about R111 is reasonable.</p>"
                    ),
                },
                'video': {'id': 'owh1AV9zTjo',
                          'title': 'Grade 10-12 Mathematical literacy (P1 & P2): Number operations',
                          'channel': 'Tz Tutoring', 'minutes': 15},
                'worksheet': {
                    'instructions': 'Show your calculations and give answers with units.',
                    'exercises': [
                        '1. Write R3,4 million in digits.',
                        '2. Calculate 25 - 3 x 4 + 8 ÷ 2.',
                        '3. Calculate (25 - 3) x (4 + 8) ÷ 2.',
                        '4. Round R1 247,68 to the nearest rand and to the nearest R100.',
                        '5. A room needs 23,4 m² of tiles. Tiles are sold in boxes of 2 m². How many boxes must you buy?',
                        '6. A minibus taxi seats 15 passengers. How many taxis are needed for 68 learners?',
                        '7. Sipho buys 4 pies at R24,90 each and pays with R200. How much change does he get?',
                    ],
                },
                'quiz': [
                    ('mcq', 'Calculate 20 - 4 x 3.', ['48', '8', '12', '4'], 1),
                    ('mcq', 'Round R47,63 to the nearest rand.', ['R47', 'R50', 'R47,60', 'R48'], 3),
                    ('tf', 'If a job needs 4,2 tins of paint, you should buy 5 tins.', True),
                    ('mcq', 'Write R2,5 million in digits.', ['R25 000', 'R250 000', 'R2 500 000', 'R25 000 000'], 2),
                ],
                'homework': {
                    'title': 'Numbers in my household',
                    'instructions': 'Use a recent till slip or advert from home (or make up realistic prices).',
                    'tasks': [
                        'List 5 items with their prices and calculate the total cost.',
                        'Estimate the total first by rounding each price to the nearest R10, then compare it with the exact total.',
                        'Calculate the change from a R500 note.',
                    ],
                    'marks': 10,
                },
            },
            {
                'title': 'Ratio, rate and proportion',
                'minutes': 45,
                'objectives': [
                    'I can simplify a ratio and share an amount in a given ratio.',
                    'I can calculate and compare rates such as speed and unit price.',
                    'I can use direct proportion to scale quantities.',
                ],
                'notes': (
                    "<p>A <strong>ratio</strong> compares quantities of the <em>same</em> kind, in the same units, "
                    "with no units in the answer. A recipe that uses 2 cups of rice to 3 cups of water has the ratio "
                    "2 : 3. Simplify a ratio by dividing both parts by the HCF: 12 : 18 = 2 : 3.</p>"
                    "<p><strong>Sharing in a ratio:</strong> add the parts, find the value of one part, then multiply. "
                    "To share R500 in the ratio 2 : 3, there are 5 parts, 1 part = R100, so the shares are R200 and R300.</p>"
                    "<p>A <strong>rate</strong> compares quantities of <em>different</em> kinds and always has units, "
                    "e.g. 80 km/h, R23,45/kg, 60 beats per minute. A rate is usually given 'per 1 unit'.</p>"
                    "<p><strong>Unit price</strong> helps us compare value for money: divide the price by the quantity.</p>"
                    "<p><strong>Direct proportion:</strong> when one quantity increases, the other increases by the same "
                    "factor. If 250 g of flour needs 4 eggs, then 750 g (3 times as much) needs 3 x 4 = 12 eggs.</p>"
                ),
                'key_terms': [
                    ('ratio', 'a comparison of two quantities of the same kind, written a : b'),
                    ('rate', 'a comparison of two quantities of different kinds, e.g. km per hour'),
                    ('unit price', 'the cost of one unit of a product, e.g. rand per kilogram'),
                    ('direct proportion', 'both quantities change by the same factor'),
                ],
                'example': {
                    'title': 'Worked example: which is the better buy?',
                    'html': (
                        "<p>Rice is sold as 2 kg for R46,90 or 5 kg for R109,99. Which is better value?</p>"
                        "<ul><li>2 kg: R46,90 ÷ 2 = R23,45 per kg</li>"
                        "<li>5 kg: R109,99 ÷ 5 = R22,00 per kg (rounded)</li></ul>"
                        "<p>The <strong>5 kg bag</strong> is cheaper per kilogram, saving about R1,45 per kg.</p>"
                        "<p><strong>Speed:</strong> a bus travels 240 km in 3 hours. Speed = 240 km ÷ 3 h = <strong>80 km/h</strong>.</p>"
                    ),
                },
                'video': {'id': '4ZL1_jKp-d4',
                          'title': 'Maths Literacy: Episode 3: Ratios, Proportion and Rate: What are Ratios? How do I write them?',
                          'channel': 'Mindset', 'minutes': 25},
                'worksheet': {
                    'instructions': 'Show all calculations.',
                    'exercises': [
                        '1. Simplify the ratio 45 : 60.',
                        '2. Share R1 200 between Lerato and Ben in the ratio 3 : 5.',
                        '3. A car uses 42 litres of petrol to travel 600 km. Calculate the rate in km per litre.',
                        '4. Washing powder: 1 kg for R54,99 or 3 kg for R149,99. Which is better value? Show why.',
                        '5. A recipe for 4 people uses 300 g of mince. How much mince is needed for 10 people?',
                        '6. A cyclist rides at 18 km/h. How far does she ride in 2,5 hours?',
                    ],
                },
                'quiz': [
                    ('mcq', 'Simplify 12 : 18.', ['3 : 2', '2 : 3', '1 : 6', '12 : 6'], 1),
                    ('mcq', 'Share R600 in the ratio 1 : 2. What is the larger share?', ['R200', 'R300', 'R400', 'R450'], 2),
                    ('tf', 'A car that travels 150 km in 2 hours has an average speed of 75 km/h.', True),
                    ('mcq', 'Which is better value? A: 500 g for R25. B: 1 kg for R45.', ['A', 'B', 'They are the same'], 1),
                ],
                'homework': {
                    'title': 'Ratio and rate in real life',
                    'instructions': 'Answer the questions in full sentences.',
                    'tasks': [
                        'Mix concentrated cooldrink and water in the ratio 1 : 4. How much concentrate do you need for 2,5 litres of mixed drink?',
                        'Compare the unit price of two sizes of the same product at home or in a shop advert.',
                        'Your heart beats 18 times in 15 seconds. Calculate your heart rate in beats per minute.',
                    ],
                    'marks': 10,
                },
            },
            {
                'title': 'Percentages in everyday life',
                'minutes': 45,
                'objectives': [
                    'I can calculate a percentage of an amount and write one amount as a percentage of another.',
                    'I can calculate percentage increase and decrease.',
                    'I can add and remove 15% VAT.',
                ],
                'notes': (
                    "<p><strong>Percent</strong> means 'per hundred': 25% = 25/100 = 0,25.</p>"
                    "<ul><li><strong>Percentage of an amount:</strong> 25% of R800 = 25/100 x 800 = R200.</li>"
                    "<li><strong>One amount as a percentage of another:</strong> (part ÷ whole) x 100. "
                    "A test mark of 36 out of 48 is 36 ÷ 48 x 100 = 75%.</li>"
                    "<li><strong>Percentage change:</strong> (change ÷ original amount) x 100. "
                    "Always divide by the <em>original</em> amount.</li></ul>"
                    "<p><strong>Discounts</strong> lower the price; <strong>increases</strong> raise it. Note that an "
                    "increase of 10% followed by a decrease of 10% does NOT return to the original amount, because the "
                    "second percentage is worked out on a different amount.</p>"
                    "<p><strong>VAT (Value-Added Tax)</strong> in South Africa is 15%.</p>"
                    "<ul><li>Price excluding VAT to including VAT: multiply by 1,15.</li>"
                    "<li>Price including VAT to excluding VAT: divide by 1,15.</li>"
                    "<li>The VAT amount in a VAT-inclusive price = price x 15/115.</li></ul>"
                ),
                'key_terms': [
                    ('percentage', 'a number out of 100'),
                    ('discount', 'an amount taken off the original price'),
                    ('VAT', 'Value-Added Tax, charged at 15% on most goods and services in South Africa'),
                ],
                'example': {
                    'title': 'Worked examples: percentages',
                    'html': (
                        "<p><strong>(a) Discount:</strong> a jacket costs R800 and is on sale at 25% off.<br>"
                        "Discount = 25% x R800 = R200. Sale price = R800 - R200 = <strong>R600</strong>.</p>"
                        "<p><strong>(b) Increase:</strong> a loaf of bread rises from R40 to R46.<br>"
                        "Increase = R6. Percentage increase = 6 ÷ 40 x 100 = <strong>15%</strong>.</p>"
                        "<p><strong>(c) VAT:</strong> a price including VAT is R345.<br>"
                        "Price excluding VAT = R345 ÷ 1,15 = <strong>R300</strong>; the VAT is R45.</p>"
                    ),
                },
                'video': {'id': 'FvbLEbIOuuA', 'title': 'Percentage Maths literacy',
                          'channel': 'Kevinmathscience', 'minutes': 10},
                'worksheet': {
                    'instructions': 'Use a calculator. Round money to the nearest cent.',
                    'exercises': [
                        '1. Calculate 15% of R640.',
                        '2. Write 42 out of 60 as a percentage.',
                        '3. A cellphone costs R3 200. It is discounted by 12%. Find the new price.',
                        '4. Taxi fare increases from R18 to R21. Calculate the percentage increase.',
                        '5. A fridge costs R6 400 excluding VAT. Calculate the price including 15% VAT.',
                        '6. A meal costs R230 including VAT. How much VAT is included?',
                        '7. A price of R500 increases by 10% and then decreases by 10%. What is the final price?',
                    ],
                },
                'quiz': [
                    ('mcq', 'What is 15% of R80?', ['R8', 'R15', 'R12', 'R1,20'], 2),
                    ('mcq', 'Write 18 out of 24 as a percentage.', ['72%', '75%', '80%', '66%'], 1),
                    ('tf', 'Increasing an amount by 50% and then decreasing the answer by 50% gives the original amount.', False),
                    ('mcq', 'An item costs R100 excluding VAT. What is the price including 15% VAT?', ['R115', 'R85', 'R100,15', 'R150'], 0),
                ],
                'homework': {
                    'title': 'Percentages at the shops',
                    'instructions': 'Find or invent a sale advert with at least two discounted items.',
                    'tasks': [
                        'Calculate the percentage discount on each item.',
                        'Calculate the VAT included in each sale price.',
                        'Decide which item gives the biggest saving in rand and which gives the biggest saving as a percentage.',
                    ],
                    'marks': 12,
                },
            },
        ],
    },

    (11, 'MLIT'): {
        'topic': 'Patterns, relationships and representations',
        'caps': 'Basic skills topics: Patterns, relationships and representations - relationships with a '
                'constant difference, direct and inverse proportion, constant ratio; representing '
                'relationships with equations, tables and graphs; working with two relationships',
        'summary': 'We describe relationships between quantities in real contexts and represent them '
                   'with formulae, tables and graphs, including comparing two options.',
        'days': [
            {
                'title': 'Linear relationships and direct proportion',
                'minutes': 45,
                'objectives': [
                    'I can identify the dependent and independent variables in a context.',
                    'I can write a formula, complete a table and draw a graph for a linear relationship.',
                    'I can tell the difference between a direct proportion and a linear relationship with a fixed cost.',
                ],
                'notes': (
                    "<p>Many real-life situations involve a <strong>relationship</strong> between two quantities. "
                    "The <strong>independent variable</strong> is the one we choose or control (e.g. hours worked, "
                    "litres bought). The <strong>dependent variable</strong> depends on it (e.g. total cost). "
                    "On a graph, the independent variable goes on the horizontal axis.</p>"
                    "<p>A relationship with a <strong>constant difference</strong> is <em>linear</em>: each time the "
                    "independent variable goes up by 1, the dependent variable changes by the same amount. Its graph "
                    "is a straight line.</p>"
                    "<ul><li><strong>Direct proportion:</strong> no fixed amount, e.g. Cost = R21,50 x litres of petrol "
                    "(example price). If you buy 0 litres you pay R0, so the graph passes through the origin. "
                    "Doubling the litres doubles the cost.</li>"
                    "<li><strong>Linear with a fixed amount:</strong> e.g. a plumber charges a call-out fee of R350 plus "
                    "R200 per hour: Cost = R350 + R200 x hours. The graph starts at R350 on the vertical axis, so it is "
                    "linear but NOT directly proportional.</li></ul>"
                    "<p>We can show a relationship in words, as a formula, as a table or as a graph. Each "
                    "representation gives the same information.</p>"
                ),
                'key_terms': [
                    ('independent variable', 'the quantity that is chosen or controlled; plotted on the horizontal axis'),
                    ('dependent variable', 'the quantity that depends on the other; plotted on the vertical axis'),
                    ('constant difference', 'the dependent variable changes by the same amount for every 1-unit step'),
                    ('direct proportion', 'a relationship where the quantities increase by the same factor; graph through the origin'),
                ],
                'example': {
                    'title': 'Worked example: the plumber',
                    'html': (
                        "<p>Cost (R) = 350 + 200 x number of hours</p>"
                        "<p>Table: 0 h = R350; 1 h = R550; 2 h = R750; 3 h = R950; 4 h = R1 150</p>"
                        "<p>The constant difference is <strong>R200 per hour</strong>.</p>"
                        "<p><strong>How long did a job costing R1 550 take?</strong><br>"
                        "1 550 = 350 + 200h, so 200h = 1 200 and <strong>h = 6 hours</strong>.</p>"
                        "<p>On the graph, plot (0; 350), (1; 550) ... and join the points with a straight line.</p>"
                    ),
                },
                'video': {'id': 'gRW3KrQvH18',
                          'title': 'Grade 11 - Patterns and Relationships Math Literacy (linear relationships)',
                          'channel': 'Watobe', 'minutes': 15},
                'worksheet': {
                    'instructions': 'An electrician charges R400 call-out plus R250 per hour.',
                    'exercises': [
                        '1. Identify the independent and dependent variables.',
                        '2. Write a formula for the total cost.',
                        '3. Complete a table for 0, 1, 2, 3, 4 and 5 hours.',
                        '4. Draw a graph of the relationship on graph paper.',
                        '5. How much will a 7-hour job cost?',
                        '6. A job cost R2 150. How many hours did it take?',
                        '7. Is this a direct proportion? Give a reason.',
                    ],
                },
                'quiz': [
                    ('mcq', 'In Cost = 350 + 200h, which is the independent variable?', ['Cost', 'h (hours)', '350', '200'], 1),
                    ('mcq', 'Using Cost = 350 + 200h, what does a 3-hour job cost?', ['R750', 'R1 050', 'R950', 'R600'], 2),
                    ('tf', 'The graph of a direct proportion is a straight line through the origin.', True),
                    ('mcq', 'A table shows litres 2; 4; 6 and cost R40; R80; R120. What type of relationship is this?',
                     ['Inverse proportion', 'Constant ratio', 'Direct proportion', 'No relationship'], 2),
                ],
                'homework': {
                    'title': 'Linear relationships around me',
                    'instructions': 'Choose a real situation with a fixed fee plus a rate (e.g. a taxi, a hiring company or an electricity bill).',
                    'tasks': [
                        'Describe the situation and write a formula for it (you may use realistic made-up values).',
                        'Draw up a table with at least 5 values.',
                        'Draw a neat graph and label the axes.',
                    ],
                    'marks': 15,
                },
            },
            {
                'title': 'Inverse proportion and constant ratio',
                'minutes': 45,
                'objectives': [
                    'I can recognise an inverse proportion and use the fact that the product stays constant.',
                    'I can draw and interpret the curved graph of an inverse proportion.',
                    'I can recognise a constant ratio (growth) pattern.',
                ],
                'notes': (
                    "<p>In an <strong>inverse proportion</strong>, as one quantity increases, the other decreases in such a "
                    "way that their <strong>product stays the same</strong>: x x y = constant.</p>"
                    "<p>Examples:</p>"
                    "<ul><li>More workers finish a job in fewer days (workers x days = constant).</li>"
                    "<li>Driving faster takes less time for the same distance (speed x time = distance).</li>"
                    "<li>Sharing a fixed amount among more people gives each person less.</li></ul>"
                    "<p>The graph of an inverse proportion is a <strong>curve</strong> that gets closer to the axes but never "
                    "touches them. Doubling one quantity halves the other.</p>"
                    "<p>Be careful: not every decreasing relationship is inverse. Check that the product is constant.</p>"
                    "<p><strong>Constant ratio:</strong> in some patterns each value is multiplied by the same number, e.g. "
                    "a bacteria population that doubles every hour: 100; 200; 400; 800. The graph curves upwards more and more "
                    "steeply. This type of pattern appears again when we study compound interest.</p>"
                ),
                'key_terms': [
                    ('inverse proportion', 'as one quantity increases the other decreases, and their product is constant'),
                    ('constant ratio', 'each value is multiplied by the same number to get the next value'),
                ],
                'example': {
                    'title': 'Worked example: building a wall',
                    'html': (
                        "<p>6 workers take 10 days to build a wall. Working at the same rate:</p>"
                        "<ul><li>Total work = 6 x 10 = 60 worker-days.</li>"
                        "<li>4 workers: 60 ÷ 4 = <strong>15 days</strong></li>"
                        "<li>12 workers: 60 ÷ 12 = <strong>5 days</strong></li></ul>"
                        "<p><strong>Travel:</strong> a 300 km trip takes 3 hours at 100 km/h, but 300 ÷ 60 = <strong>5 hours</strong> at 60 km/h.</p>"
                    ),
                },
                'video': {'id': 'K7h4l4OGr8I', 'title': 'Direct and Indirect Proportion',
                          'channel': 'Kevinmathscience', 'minutes': 10},
                'worksheet': {
                    'instructions': 'Show all calculations.',
                    'exercises': [
                        '1. A prize of R12 000 is shared equally. Complete a table for 1, 2, 3, 4, 6 and 8 winners.',
                        '2. Draw the graph for question 1. Describe its shape.',
                        '3. 8 taps fill a tank in 6 hours. How long would 3 taps take?',
                        '4. A trip takes 4 hours at 90 km/h. How long would it take at 120 km/h?',
                        '5. Decide whether this is inverse proportion: x = 2, 4, 5 and y = 10, 5, 4. Explain.',
                        '6. A population of 500 doubles every year. Write down the population for the next 4 years.',
                    ],
                },
                'quiz': [
                    ('mcq', '5 painters take 12 days to paint a school. How long would 10 painters take?', ['24 days', '6 days', '12 days', '5 days'], 1),
                    ('tf', 'In an inverse proportion, the product of the two quantities stays constant.', True),
                    ('mcq', 'Which table shows an inverse proportion?',
                     ['x: 1, 2, 4 and y: 8, 10, 14', 'x: 1, 2, 4 and y: 8, 16, 32', 'x: 1, 2, 4 and y: 8, 4, 2'], 2),
                    ('mcq', 'How long does a 240 km trip take at 80 km/h?', ['3 h', '4 h', '2 h', '320 h'], 0),
                ],
                'homework': {
                    'title': 'Inverse proportion problems',
                    'instructions': 'Answer each question and show your method.',
                    'tasks': [
                        'A school hall can be cleaned by 4 cleaners in 3 hours. How long would 6 cleaners take?',
                        'A bag of 60 sweets is shared equally. Complete a table for 2, 3, 4, 5 and 6 children and draw the graph.',
                        'Explain in your own words the difference between direct and inverse proportion, with one example of each.',
                    ],
                    'marks': 12,
                },
            },
            {
                'title': 'Working with two relationships',
                'minutes': 50,
                'objectives': [
                    'I can represent two options with formulae, a table and graphs on the same set of axes.',
                    'I can find and interpret the point where two graphs intersect.',
                    'I can use the representations to decide which option is better.',
                ],
                'notes': (
                    "<p>Often we must compare two options, such as two cellphone contracts, two gyms or two taxi "
                    "companies. Each option is a relationship, and we can show both on the same set of axes.</p>"
                    "<p><strong>Steps:</strong></p>"
                    "<ol><li>Write a formula for each option.</li>"
                    "<li>Complete a table of values for both options using the same inputs.</li>"
                    "<li>Draw both graphs on the same axes with a clear key.</li>"
                    "<li>Find the <strong>point of intersection</strong>: the input where both options give the same output. "
                    "You can read it from the graph, find it in the table, or set the formulae equal to each other.</li>"
                    "<li>Interpret: one option is cheaper before the intersection and the other is cheaper after it.</li></ol>"
                    "<p>The same idea is used to find a <strong>break-even point</strong> in business, where income equals "
                    "costs.</p>"
                    "<p>Always answer the question in words: 'Gym A is cheaper if you stay for more than 6 months.'</p>"
                ),
                'key_terms': [
                    ('point of intersection', 'where two graphs cross; both relationships give the same output there'),
                    ('break-even point', 'where income equals expenses, so there is no profit or loss'),
                ],
                'example': {
                    'title': 'Worked example: choosing a gym',
                    'html': (
                        "<p>Gym A: R300 joining fee plus R150 per month. Gym B: no joining fee, R200 per month.</p>"
                        "<p>Cost A = 300 + 150m &nbsp; and &nbsp; Cost B = 200m</p>"
                        "<p>Table (months 0; 2; 4; 6; 8):<br>A: R300; R600; R900; R1 200; R1 500<br>"
                        "B: R0; R400; R800; R1 200; R1 600</p>"
                        "<p><strong>Equal cost:</strong> 300 + 150m = 200m, so 50m = 300 and m = 6. "
                        "Both cost R1 200 after 6 months.</p>"
                        "<p><strong>Conclusion:</strong> Gym B is cheaper for less than 6 months; Gym A is cheaper for more than 6 months.</p>"
                    ),
                },
                'video': {'id': '6U2oHjohRgE',
                          'title': 'Grade 11 - Patterns and Relationships Math Literacy (tables, graphs and formulae)',
                          'channel': 'Watobe', 'minutes': 15},
                'worksheet': {
                    'instructions': 'Taxi X charges R20 plus R12 per km. Taxi Y charges R16 per km with no fixed fee.',
                    'exercises': [
                        '1. Write a formula for the cost of each taxi.',
                        '2. Complete a table for 0, 2, 4, 5, 6, 8 and 10 km for both taxis.',
                        '3. Draw both graphs on the same set of axes.',
                        '4. For what distance do both taxis cost the same?',
                        '5. Which taxi is cheaper for an 8 km trip? By how much?',
                        '6. Write a short recommendation for a learner who travels 3 km to school.',
                    ],
                },
                'quiz': [
                    ('mcq', 'Gym A = 300 + 150m and Gym B = 200m. After how many months is the cost equal?', ['4', '6', '8', '3'], 1),
                    ('mcq', 'Using Gym B = 200m, what is the cost of Gym B for 10 months?', ['R1 800', 'R1 500', 'R2 000', 'R2 100'], 2),
                    ('tf', 'At the point where two cost graphs intersect, both options cost the same.', True),
                    ('mcq', 'For 10 months, which gym is cheaper?', ['Gym A', 'Gym B', 'They cost the same'], 0),
                ],
                'homework': {
                    'title': 'Compare two options',
                    'instructions': 'Two printing shops: Shop P charges R50 set-up plus R2 per page; Shop Q charges R4,50 per page.',
                    'tasks': [
                        'Write a formula for each shop and complete a table for 0 to 40 pages in steps of 10.',
                        'Draw both graphs on one set of axes and find where they intersect.',
                        'Advise someone who needs to print 30 pages which shop to use, with reasons.',
                    ],
                    'marks': 15,
                },
            },
        ],
    },

    (12, 'MLIT'): {
        'topic': 'Finance: financial documents',
        'caps': 'Finance: Financial documents - personal and household documents (till slips, invoices, '
                'quotations, account statements, payslips and bank statements); interpreting the '
                'information and performing calculations from them',
        'summary': 'We read and work with financial documents: till slips and invoices, payslips, and '
                   'bank statements.',
        'days': [
            {
                'title': 'Till slips, invoices and quotations',
                'minutes': 45,
                'objectives': [
                    'I can identify the purpose and key parts of till slips, invoices and quotations.',
                    'I can check the calculations on a financial document.',
                    'I can calculate VAT included in an amount and VAT to be added.',
                ],
                'notes': (
                    "<p>Financial documents record money that is spent, owed or received. Being able to read them "
                    "helps you avoid mistakes and manage your money.</p>"
                    "<ul><li><strong>Till slip:</strong> proof of payment from a shop. It shows the items, prices, "
                    "total, VAT included, amount tendered, change and the payment method.</li>"
                    "<li><strong>Quotation:</strong> an estimate of the cost <em>before</em> goods or services are "
                    "provided. It usually has an expiry date.</li>"
                    "<li><strong>Invoice:</strong> a request for payment for goods or services that have been "
                    "supplied. It shows the quantity, unit price, subtotal, VAT and total due.</li>"
                    "<li><strong>Account statement:</strong> a summary of transactions over a period, with an opening "
                    "balance, payments, new charges and closing balance.</li></ul>"
                    "<p><strong>VAT (15%)</strong>: on an invoice, VAT = 15% x subtotal. On a till slip the prices "
                    "usually <em>include</em> VAT, so the VAT portion = total x 15/115.</p>"
                    "<p>Always check: quantity x unit price = amount, and the amounts add up to the subtotal.</p>"
                ),
                'key_terms': [
                    ('invoice', 'a document requesting payment for goods or services supplied'),
                    ('quotation', 'an estimate of the cost of goods or services before the work is done'),
                    ('subtotal', 'the total before VAT or other charges are added'),
                    ('amount tendered', 'the money handed over to pay'),
                ],
                'example': {
                    'title': 'Worked example: checking an invoice',
                    'html': (
                        "<p>A small business is invoiced for 3 printer cartridges at R120 each and 2 reams of paper at R85 each.</p>"
                        "<ul><li>Cartridges: 3 x R120 = R360,00</li>"
                        "<li>Paper: 2 x R85 = R170,00</li>"
                        "<li>Subtotal: R530,00</li>"
                        "<li>VAT at 15%: 0,15 x R530 = R79,50</li>"
                        "<li><strong>Total due: R609,50</strong></li></ul>"
                        "<p><strong>Till slip:</strong> a till slip total is R460,00 including VAT. VAT included = R460 x 15/115 = <strong>R60,00</strong>.</p>"
                    ),
                },
                'video': {'id': '1tW7gt497sA', 'title': 'Grade 12 Maths Literacy Finance: Financial documents',
                          'channel': 'Distance learning with Lee', 'minutes': 20},
                'worksheet': {
                    'instructions': 'A quotation from a builder lists: 40 bags of cement at R98,50 each, 2 000 bricks at R3,20 each and labour of R6 500 (all excluding VAT).',
                    'exercises': [
                        '1. Calculate the cost of the cement.',
                        '2. Calculate the cost of the bricks.',
                        '3. Calculate the subtotal.',
                        '4. Calculate the VAT at 15% and the total amount quoted.',
                        '5. The quotation is valid for 30 days from 14 January. On what date does it expire?',
                        '6. A till slip shows a total of R1 035 including VAT. How much VAT was paid?',
                        '7. Explain the difference between a quotation and an invoice.',
                    ],
                },
                'quiz': [
                    ('mcq', 'How much VAT is included in a price of R230 (VAT inclusive)?', ['R30', 'R34,50', 'R23', 'R15'], 0),
                    ('tf', 'An invoice is a document that requests payment for goods or services supplied.', True),
                    ('mcq', 'Which document shows the deductions from an employee\'s salary?', ['Till slip', 'Invoice', 'Quotation', 'Payslip'], 3),
                    ('mcq', 'What is a quotation?', ['Proof that payment was made', 'An estimate of cost before the work is done', 'A monthly summary of a bank account'], 1),
                ],
                'homework': {
                    'title': 'Analyse a till slip',
                    'instructions': 'Use a real till slip from home (cover any personal details) or one given by your teacher.',
                    'tasks': [
                        'List all the information that appears on the slip (shop, date, items, total, VAT, payment method).',
                        'Check the total by adding the items.',
                        'Calculate the VAT included and compare it with the amount printed on the slip.',
                    ],
                    'marks': 10,
                },
            },
            {
                'title': 'Payslips: gross pay, deductions and net pay',
                'minutes': 45,
                'objectives': [
                    'I can identify gross income, deductions and net income on a payslip.',
                    'I can calculate UIF and percentage-based deductions.',
                    'I can calculate net pay and check a payslip for errors.',
                ],
                'notes': (
                    "<p>A <strong>payslip</strong> is given to an employee each pay period. It shows how the take-home pay was worked out.</p>"
                    "<ul><li><strong>Gross income:</strong> the total earned before deductions (basic salary plus overtime, "
                    "commission or allowances).</li>"
                    "<li><strong>Deductions:</strong> amounts taken off, such as:<ul>"
                    "<li><strong>PAYE</strong> (Pay As You Earn): income tax paid to SARS by the employer on the employee's behalf.</li>"
                    "<li><strong>UIF</strong> (Unemployment Insurance Fund): the employee pays 1% of gross remuneration and the "
                    "employer adds another 1%. UIF is calculated on earnings up to a monthly ceiling set by government.</li>"
                    "<li>Pension or retirement fund contributions (often a percentage of the basic salary).</li>"
                    "<li>Medical aid, union fees, loans.</li></ul></li>"
                    "<li><strong>Net income</strong> (take-home pay) = gross income - total deductions.</li></ul>"
                    "<p>Some items are <em>employer contributions</em> (e.g. the employer's 1% UIF). These are shown on the "
                    "payslip for information but are not deducted from your pay.</p>"
                ),
                'key_terms': [
                    ('gross income', 'total earnings before any deductions'),
                    ('net income', 'take-home pay after all deductions'),
                    ('PAYE', 'Pay As You Earn: income tax deducted from a salary each month'),
                    ('UIF', 'Unemployment Insurance Fund: 1% from the employee plus 1% from the employer'),
                ],
                'example': {
                    'title': 'Worked example: calculating net pay',
                    'html': (
                        "<p>Ms Dlamini earns a gross salary of R12 000 per month. Her deductions are:</p>"
                        "<ul><li>UIF: 1% x R12 000 = R120,00</li>"
                        "<li>PAYE (given on the payslip): R1 050,00</li>"
                        "<li>Pension: 7,5% x R12 000 = R900,00</li>"
                        "<li>Medical aid: R1 400,00</li></ul>"
                        "<p>Total deductions = R120 + R1 050 + R900 + R1 400 = R3 470,00</p>"
                        "<p><strong>Net pay = R12 000 - R3 470 = R8 530,00</strong></p>"
                        "<p>Her deductions are 3 470 ÷ 12 000 x 100 = about 28,9% of her gross pay.</p>"
                    ),
                },
                'video': {'id': 'xcBiXhP-AIk',
                          'title': 'Grade 12 Maths Literacy Finance: Financial documents | Salary slip analysis',
                          'channel': 'Distance learning with Lee', 'minutes': 20},
                'worksheet': {
                    'instructions': 'Mr Botha earns a basic salary of R14 500 and worked overtime worth R1 300 this month. PAYE is R1 640.',
                    'exercises': [
                        '1. Calculate his gross income.',
                        '2. Calculate his UIF contribution (1% of gross income).',
                        '3. His pension contribution is 6% of his basic salary. Calculate it.',
                        '4. He also pays R980 for medical aid. Calculate his total deductions.',
                        '5. Calculate his net income.',
                        '6. What percentage of his gross income does he take home? Round to one decimal place.',
                        '7. How much UIF does his employer contribute for him?',
                    ],
                },
                'quiz': [
                    ('mcq', 'A worker earns a gross income of R9 000. What is her UIF contribution at 1%?', ['R9', 'R90', 'R900', 'R0,90'], 1),
                    ('tf', 'Net pay is always higher than gross pay.', False),
                    ('mcq', 'Gross income is R15 000 and total deductions are R3 200. What is the net income?', ['R18 200', 'R12 800', 'R11 800', 'R3 200'], 2),
                    ('mcq', 'What does PAYE stand for?', ['Pay As You Earn', 'Paid After Your Expenses', 'Payment And Yearly Earnings'], 0),
                ],
                'homework': {
                    'title': 'Payslip check',
                    'instructions': 'A payslip shows: basic R10 500, overtime R750, UIF R112,50, PAYE R820, pension R787,50, net pay R9 630.',
                    'tasks': [
                        'Calculate the gross income.',
                        'Check that the UIF is 1% of gross income.',
                        'Calculate the total deductions and the correct net pay.',
                        'Is the net pay on the payslip correct? Explain.',
                    ],
                    'marks': 12,
                },
            },
            {
                'title': 'Bank statements',
                'minutes': 45,
                'objectives': [
                    'I can identify the opening balance, credits, debits, fees and closing balance on a bank statement.',
                    'I can calculate a running balance.',
                    'I can interpret transactions such as debit orders and bank charges.',
                ],
                'notes': (
                    "<p>A <strong>bank statement</strong> lists every transaction on an account over a period (usually a month).</p>"
                    "<ul><li><strong>Opening balance:</strong> the money in the account at the start of the period.</li>"
                    "<li><strong>Credits (deposits):</strong> money coming in, e.g. salary or a transfer. Credits increase the balance.</li>"
                    "<li><strong>Debits (withdrawals):</strong> money going out, e.g. card purchases, ATM withdrawals, "
                    "<strong>debit orders</strong> (automatic payments you have authorised, such as insurance) and "
                    "<strong>stop orders</strong>. Debits decrease the balance.</li>"
                    "<li><strong>Bank charges:</strong> fees the bank charges for services, such as a monthly account fee "
                    "or a fee per ATM withdrawal.</li>"
                    "<li><strong>Closing balance:</strong> opening balance + credits - debits.</li></ul>"
                    "<p>If the balance becomes negative, the account is <strong>overdrawn</strong> (often shown with 'Dr' "
                    "or a minus sign) and the bank may charge interest and penalties.</p>"
                    "<p>Check your statement every month for errors or transactions you did not make.</p>"
                ),
                'key_terms': [
                    ('credit', 'money paid into an account'),
                    ('debit', 'money paid out of an account'),
                    ('debit order', 'an automatic payment from your account that you have authorised'),
                    ('overdrawn', 'when the account balance is below zero'),
                ],
                'example': {
                    'title': 'Worked example: a running balance',
                    'html': (
                        "<p>Opening balance: R2 450,00</p>"
                        "<ul><li>Salary credit +R8 500,00: balance R10 950,00</li>"
                        "<li>Debit order (insurance) -R385,00: balance R10 565,00</li>"
                        "<li>ATM withdrawal -R1 000,00: balance R9 565,00</li>"
                        "<li>ATM fee -R10,50: balance R9 554,50</li>"
                        "<li>Card purchase (groceries) -R1 236,40: balance R8 318,10</li></ul>"
                        "<p><strong>Closing balance: R8 318,10</strong></p>"
                        "<p>Total debits = R385 + R1 000 + R10,50 + R1 236,40 = R2 631,90. Check: R2 450 + R8 500 - R2 631,90 = R8 318,10.</p>"
                    ),
                },
                'video': {'id': 'F4WooZTGGeg',
                          'title': 'Grade 12 Maths Literacy Finance: Financial documents | Bank Statements',
                          'channel': 'Distance learning with Lee', 'minutes': 20},
                'worksheet': {
                    'instructions': 'Opening balance R1 820,00. Transactions: salary +R7 400,00; rent -R3 500,00; cellphone debit order -R399,00; ATM withdrawal -R800,00; ATM fee -R9,80; monthly fee -R65,00.',
                    'exercises': [
                        '1. Calculate the running balance after each transaction.',
                        '2. What is the closing balance?',
                        '3. Calculate the total bank charges.',
                        '4. Calculate the total of all debits.',
                        '5. What percentage of the salary is spent on rent? Round to one decimal place.',
                        '6. Explain what would happen if the opening balance had been R0 and the salary was paid after the rent.',
                    ],
                },
                'quiz': [
                    ('tf', 'A credit on a bank statement increases the balance.', True),
                    ('mcq', 'Opening balance R500, deposit R300, withdrawal R200. What is the closing balance?', ['R1 000', 'R400', 'R600', 'R0'], 2),
                    ('mcq', 'What is a debit order?', ['Money you deposit at the bank', 'An automatic payment from your account that you authorised', 'Interest the bank pays you'], 1),
                    ('mcq', 'What does a negative balance on a bank statement mean?', ['The account is overdrawn', 'The account earned interest', 'The account has been closed'], 0),
                ],
                'homework': {
                    'title': 'Plan a month on a bank statement',
                    'instructions': 'Imagine you start working and earn R8 000 per month. Use realistic amounts.',
                    'tasks': [
                        'List at least six debits you would expect in a month (rent, transport, food, airtime, fees, savings).',
                        'Set out a bank statement with a running balance, starting from an opening balance of R500.',
                        'Calculate the closing balance and say whether you could save money that month.',
                    ],
                    'marks': 15,
                },
            },
        ],
    },

    # =====================================================================
    # PHYSICAL SCIENCES
    # =====================================================================
    (10, 'PHYS-SCI'): {
        'topic': 'Matter and materials: classification of matter',
        'caps': 'Matter and materials: Revise matter and classification - the materials of which objects '
                'are made; mixtures (heterogeneous and homogeneous); pure substances (elements and '
                'compounds); names and formulae of substances; metals, metalloids and non-metals; '
                'electrical and thermal conductors and insulators; magnetic and non-magnetic materials',
        'summary': 'We classify matter into mixtures and pure substances, name and write formulae for '
                   'compounds, and classify materials by their properties.',
        'days': [
            {
                'title': 'Mixtures and pure substances',
                'minutes': 50,
                'objectives': [
                    'I can classify matter as a mixture or a pure substance.',
                    'I can distinguish between homogeneous and heterogeneous mixtures.',
                    'I can suggest a method to separate a mixture based on the properties of its parts.',
                ],
                'notes': (
                    "<p>Everything around us is made of <strong>matter</strong>: anything that has mass and takes up space. "
                    "Chemists classify matter by its composition.</p>"
                    "<p>A <strong>mixture</strong> contains two or more substances that are <em>not</em> chemically bonded. "
                    "The parts keep their own properties and can be present in any proportion.</p>"
                    "<ul><li><strong>Heterogeneous mixture:</strong> not uniform; you can see the different parts, e.g. sand and "
                    "water, granite, salad dressing.</li>"
                    "<li><strong>Homogeneous mixture:</strong> uniform throughout; the parts cannot be seen separately, e.g. salt "
                    "water, air, brass (an alloy of copper and zinc). A homogeneous mixture of a solute in a solvent is a "
                    "<strong>solution</strong>.</li></ul>"
                    "<p>A <strong>pure substance</strong> has a fixed composition and fixed properties such as a sharp melting "
                    "point and boiling point. Pure substances are either <strong>elements</strong> or <strong>compounds</strong>.</p>"
                    "<p>Mixtures can be separated by <strong>physical methods</strong>: filtration (insoluble solid from a liquid), "
                    "evaporation (dissolved solid from a solution), distillation (liquids with different boiling points), "
                    "a magnet (iron from other solids), and paper chromatography (dyes).</p>"
                ),
                'key_terms': [
                    ('mixture', 'two or more substances physically combined, not chemically bonded'),
                    ('homogeneous', 'uniform composition throughout'),
                    ('heterogeneous', 'non-uniform; different parts can be seen'),
                    ('pure substance', 'matter with a fixed composition and definite properties'),
                ],
                'example': {
                    'title': 'Class activity: classify these substances',
                    'html': (
                        "<ul><li>Air: <strong>homogeneous mixture</strong> (mainly nitrogen and oxygen)</li>"
                        "<li>Sand and water: <strong>heterogeneous mixture</strong>; separate by filtration</li>"
                        "<li>Distilled water: <strong>pure substance (compound)</strong>, H2O</li>"
                        "<li>Copper wire: <strong>pure substance (element)</strong>, Cu</li>"
                        "<li>Brass: <strong>homogeneous mixture</strong> (alloy)</li>"
                        "<li>Table salt: <strong>pure substance (compound)</strong>, NaCl</li>"
                        "<li>Salt water: <strong>homogeneous mixture</strong>; recover the salt by evaporation</li></ul>"
                    ),
                },
                'video': {'id': 'gVkuCfkpd_I',
                          'title': 'Grade 10 Pure Substances vs Mixtures: Classification of matter Chemistry',
                          'channel': 'Miss Martins Maths and Science', 'minutes': 12},
                'worksheet': {
                    'instructions': 'Classify each substance and give a reason. Name a separation method where asked.',
                    'exercises': [
                        '1. Tap water: pure substance or mixture?',
                        '2. Oxygen gas: element, compound or mixture?',
                        '3. Soil: homogeneous or heterogeneous mixture?',
                        '4. Sugar dissolved in tea: homogeneous or heterogeneous?',
                        '5. Name a method to separate iron filings from sulfur powder.',
                        '6. Name a method to separate ethanol from water.',
                        '7. Why does a pure substance have a sharp melting point but a mixture melts over a range of temperatures?',
                    ],
                },
                'quiz': [
                    ('mcq', 'How is air classified?', ['Element', 'Compound', 'Homogeneous mixture', 'Heterogeneous mixture'], 2),
                    ('tf', 'A pure substance has a fixed melting point.', True),
                    ('mcq', 'What is the best way to separate iron filings from sand?', ['Filtration', 'Using a magnet', 'Evaporation', 'Distillation'], 1),
                    ('mcq', 'Which of these is a heterogeneous mixture?', ['Salt water', 'Brass', 'Air', 'Granite'], 3),
                ],
                'homework': {
                    'title': 'Mixtures at home',
                    'instructions': 'Look around your kitchen and bathroom.',
                    'tasks': [
                        'List 4 homogeneous mixtures and 4 heterogeneous mixtures you find.',
                        'Choose one heterogeneous mixture and describe how you could separate it.',
                        'Name two pure substances found in a home and say whether each is an element or a compound.',
                    ],
                    'marks': 10,
                },
            },
            {
                'title': 'Elements, compounds, names and formulae',
                'minutes': 50,
                'objectives': [
                    'I can define an element and a compound and give examples.',
                    'I can name simple compounds from their formulae.',
                    'I can write chemical formulae using the charges of ions, including polyatomic ions.',
                ],
                'notes': (
                    "<p>An <strong>element</strong> is a pure substance made of only one type of atom. It cannot be broken down "
                    "into simpler substances by chemical means. Elements are listed on the <strong>periodic table</strong> "
                    "(118 known elements), e.g. Fe (iron), O (oxygen), Na (sodium).</p>"
                    "<p>A <strong>compound</strong> is a pure substance made of two or more different elements chemically "
                    "bonded in a <strong>fixed ratio</strong>, e.g. water H2O always has 2 hydrogen atoms for every oxygen atom. "
                    "A compound's properties differ from those of its elements.</p>"
                    "<p><strong>Naming compounds:</strong></p>"
                    "<ul><li>Metal + non-metal: name the metal, then the non-metal ending in <em>-ide</em>: NaCl is sodium chloride, "
                    "MgO is magnesium oxide.</li>"
                    "<li>Two non-metals: use prefixes (mono-, di-, tri-, tetra-): CO is carbon monoxide, CO2 is carbon dioxide.</li>"
                    "<li><strong>Polyatomic ions</strong> keep their names: hydroxide OH(-), nitrate NO3(-), sulfate SO4(2-), "
                    "carbonate CO3(2-), ammonium NH4(+).</li></ul>"
                    "<p><strong>Writing formulae:</strong> the total positive charge must equal the total negative charge. "
                    "Calcium is Ca(2+) and chloride is Cl(-), so calcium chloride is CaCl2. Use brackets for more than one "
                    "polyatomic ion: calcium hydroxide is Ca(OH)2.</p>"
                ),
                'key_terms': [
                    ('element', 'a pure substance made of one type of atom'),
                    ('compound', 'a pure substance of two or more elements chemically bonded in a fixed ratio'),
                    ('polyatomic ion', 'a charged group of atoms that act as one unit, e.g. SO4(2-)'),
                    ('chemical formula', 'symbols and numbers showing the elements and ratio of atoms in a substance'),
                ],
                'example': {
                    'title': 'Worked examples: writing formulae',
                    'html': (
                        "<p><strong>(a) Aluminium oxide:</strong> Al(3+) and O(2-). The lowest common multiple of 3 and 2 is 6, "
                        "so 2 Al(3+) (+6) balance 3 O(2-) (-6). Formula: <strong>Al2O3</strong>.</p>"
                        "<p><strong>(b) Sodium sulfate:</strong> Na(+) and SO4(2-). Two Na(+) balance one SO4(2-). "
                        "Formula: <strong>Na2SO4</strong>.</p>"
                        "<p><strong>(c) Name KNO3:</strong> K is potassium and NO3 is nitrate, so <strong>potassium nitrate</strong>.</p>"
                        "<p><strong>(d) Count atoms in H2SO4:</strong> 2 H + 1 S + 4 O = <strong>7 atoms</strong>.</p>"
                    ),
                },
                'video': {'id': 'BDcovT3Nxlw', 'title': '1) Atoms compounds elements and molecules gr 10',
                          'channel': 'Kevinmathscience', 'minutes': 8},
                'worksheet': {
                    'instructions': 'Write the formula or the name of each substance.',
                    'exercises': [
                        '1. Write the formula: potassium bromide',
                        '2. Write the formula: magnesium chloride',
                        '3. Write the formula: ammonium sulfate',
                        '4. Write the formula: copper(II) hydroxide',
                        '5. Name: CaCO3',
                        '6. Name: SO2',
                        '7. Name: Na2O',
                        '8. Is NH3 an element or a compound? How many atoms are in one molecule?',
                    ],
                },
                'quiz': [
                    ('mcq', 'What is the formula of magnesium oxide?', ['MgO2', 'MgO', 'Mg2O', 'Mg2O3'], 1),
                    ('tf', 'CO2 is an element.', False),
                    ('mcq', 'What is the name of KNO3?', ['Potassium nitride', 'Potassium nitrite', 'Potassium nitrogen trioxide', 'Potassium nitrate'], 3),
                    ('mcq', 'How many atoms are there in one H2SO4 unit?', ['3', '6', '7', '4'], 2),
                ],
                'homework': {
                    'title': 'Names and formulae',
                    'instructions': 'Use a periodic table and a table of ion charges.',
                    'tasks': [
                        'Write formulae for: sodium carbonate, iron(III) oxide, calcium nitrate.',
                        'Name: AlCl3, NaOH, CuSO4.',
                        'Explain in two sentences why water is a compound but oxygen gas is an element.',
                    ],
                    'marks': 12,
                },
            },
            {
                'title': 'Properties of materials: metals, conductors and magnetism',
                'minutes': 50,
                'objectives': [
                    'I can classify elements as metals, metalloids or non-metals using the periodic table and properties.',
                    'I can classify materials as electrical conductors, semiconductors or insulators.',
                    'I can identify thermal conductors and insulators and magnetic materials, and choose materials for a use.',
                ],
                'notes': (
                    "<p>We choose materials for objects based on their <strong>properties</strong>.</p>"
                    "<p><strong>Metals</strong> (left of the staircase line on the periodic table) are shiny (lustrous), malleable "
                    "(can be hammered into sheets), ductile (can be drawn into wires), and good conductors of heat and electricity. "
                    "Examples: copper, iron, aluminium.</p>"
                    "<p><strong>Non-metals</strong> (right of the line) are usually dull, brittle when solid, and poor conductors. "
                    "Examples: sulfur, oxygen, carbon (graphite is an exception: it conducts electricity).</p>"
                    "<p><strong>Metalloids</strong> lie along the staircase line and have properties of both, e.g. silicon and "
                    "germanium. Silicon is a <strong>semiconductor</strong>: it conducts electricity better than an insulator but "
                    "worse than a metal, which makes it vital for computer chips and solar cells.</p>"
                    "<ul><li><strong>Electrical conductors</strong> allow charge to flow (copper wire); <strong>insulators</strong> do "
                    "not (plastic, rubber, glass).</li>"
                    "<li><strong>Thermal conductors</strong> transfer heat easily (metals); <strong>thermal insulators</strong> do not "
                    "(wood, plastic, air, polystyrene).</li>"
                    "<li><strong>Magnetic materials</strong> are attracted to a magnet: iron, cobalt, nickel and their alloys such as "
                    "steel. Most metals (copper, aluminium, gold) are NOT magnetic.</li></ul>"
                ),
                'key_terms': [
                    ('malleable', 'can be hammered into thin sheets'),
                    ('ductile', 'can be drawn out into wires'),
                    ('metalloid', 'an element with properties of both metals and non-metals'),
                    ('semiconductor', 'a material whose electrical conductivity is between a conductor and an insulator'),
                ],
                'example': {
                    'title': 'Class activity: design a cooking pot',
                    'html': (
                        "<p>Choose materials for each part of a pot and give a reason.</p>"
                        "<ul><li><strong>Pot body:</strong> stainless steel or aluminium: good thermal conductors, so heat reaches the food quickly; strong and malleable.</li>"
                        "<li><strong>Handle:</strong> wood or heat-resistant plastic: thermal insulators, so the handle stays cool enough to hold.</li>"
                        "<li><strong>Electric kettle cable:</strong> copper wire (electrical conductor) covered in plastic (electrical insulator) for safety.</li></ul>"
                        "<p>Test: bring a magnet near a steel pot and an aluminium pot. Only the steel pot is attracted, because steel contains iron.</p>"
                    ),
                },
                'video': {'id': '5M4hJjp3-lQ', 'title': 'Grade 10 Classification of Matter: Properties of materials',
                          'channel': 'Miss Martins Maths and Science', 'minutes': 12},
                'worksheet': {
                    'instructions': 'Answer each question with a reason.',
                    'exercises': [
                        '1. Classify as metal, metalloid or non-metal: magnesium, boron, chlorine, silicon, zinc, phosphorus.',
                        '2. Give three physical properties of metals.',
                        '3. Why are electrical wires made of copper and coated in plastic?',
                        '4. Which materials are magnetic: iron nail, copper coin, aluminium can, nickel, steel paperclip?',
                        '5. Why are many cooler boxes made of polystyrene?',
                        '6. Why is silicon used in solar panels and computer chips?',
                    ],
                },
                'quiz': [
                    ('mcq', 'Which of these elements is a metalloid?', ['Sodium', 'Silicon', 'Sulfur', 'Copper'], 1),
                    ('tf', 'All metals are magnetic.', False),
                    ('mcq', 'Which is the best material for a pot handle?', ['Copper', 'Aluminium', 'Wood', 'Iron'], 2),
                    ('mcq', 'Which of these metals is attracted to a magnet?', ['Nickel', 'Aluminium', 'Copper', 'Gold'], 0),
                ],
                'homework': {
                    'title': 'Materials survey',
                    'instructions': 'Choose five objects at home made from different materials.',
                    'tasks': [
                        'Draw up a table: object, material, metal or non-metal, conductor or insulator (heat and electricity), magnetic or not.',
                        'For two of the objects, explain why that material was a good choice.',
                    ],
                    'marks': 10,
                },
            },
        ],
    },

    (11, 'PHYS-SCI'): {
        'topic': 'Mechanics: vectors in two dimensions',
        'caps': 'Mechanics: Vectors in two dimensions - resultant of perpendicular vectors (head-to-tail '
                'and tail-to-tail methods, Pythagoras and trigonometry); resolution of a vector into its '
                'parallel and perpendicular components',
        'summary': 'We revise vectors and scalars, find the resultant of perpendicular vectors and resolve '
                   'vectors into components.',
        'days': [
            {
                'title': 'Vectors, scalars and resultants in one dimension',
                'minutes': 50,
                'objectives': [
                    'I can distinguish between vector and scalar quantities.',
                    'I can describe the direction of a vector using compass directions and bearings.',
                    'I can find the resultant of vectors that act along the same line.',
                ],
                'notes': (
                    "<p>A <strong>scalar</strong> has magnitude (size) only, e.g. mass, time, distance, speed, energy. "
                    "A <strong>vector</strong> has magnitude <em>and</em> direction, e.g. displacement, velocity, acceleration, force.</p>"
                    "<p><strong>Representing vectors:</strong> draw an arrow to scale. The length shows the magnitude and the "
                    "arrowhead shows the direction. In text, a vector is written in bold (F) or with an arrow above it.</p>"
                    "<p><strong>Describing direction:</strong></p>"
                    "<ul><li>Compass directions: north, east, south, west, or e.g. 30° east of north.</li>"
                    "<li>Bearings: measured <strong>clockwise from north</strong>, written with three digits. North = 000°, "
                    "east = 090°, south = 180°, west = 270°.</li></ul>"
                    "<p>Two vectors are <strong>equal</strong> if they have the same magnitude and direction. The "
                    "<strong>negative</strong> of a vector has the same magnitude but the opposite direction.</p>"
                    "<p>The <strong>resultant</strong> is the single vector that has the same effect as all the vectors acting "
                    "together. For vectors along one line, choose a positive direction, give opposite vectors a negative sign, "
                    "and add. Always give the resultant's magnitude AND direction.</p>"
                ),
                'key_terms': [
                    ('scalar', 'a physical quantity with magnitude only'),
                    ('vector', 'a physical quantity with magnitude and direction'),
                    ('resultant', 'the single vector with the same effect as two or more vectors together'),
                    ('bearing', 'a direction measured clockwise from north, written with three digits'),
                ],
                'example': {
                    'title': 'Worked example: forces on a box',
                    'html': (
                        "<p>Two learners push a box east with forces of 40 N and 25 N. A third learner pushes west with 30 N.</p>"
                        "<p>Take east as positive.</p>"
                        "<p>F(net) = (+40) + (+25) + (-30) = +35 N</p>"
                        "<p><strong>Resultant = 35 N east.</strong></p>"
                        "<p>A girl walks 4 m east then 3 m west. Her displacement is 1 m east, but the distance she walked is 7 m.</p>"
                    ),
                },
                'video': {'id': '2yB6px0fnYU', 'title': 'Grade 11 Resultant vector and Vector Directions',
                          'channel': 'Miss Martins Maths and Science', 'minutes': 12},
                'worksheet': {
                    'instructions': 'Answer the questions. Show your sign convention.',
                    'exercises': [
                        '1. Classify as vector or scalar: velocity, mass, weight, temperature, displacement, work.',
                        '2. Give the bearing for: north-east, south, west, south-west.',
                        '3. Find the resultant of 12 N north and 7 N south.',
                        '4. Find the resultant of 5 N left, 9 N right and 2 N left.',
                        '5. A car drives 8 km west and then 3 km east. Find its displacement and distance travelled.',
                        '6. Draw, to scale (1 cm = 10 N), a force of 45 N on a bearing of 060°.',
                    ],
                },
                'quiz': [
                    ('mcq', 'Which of these is a vector quantity?', ['Mass', 'Speed', 'Displacement', 'Time'], 2),
                    ('tf', 'A bearing of 090° points due east.', True),
                    ('mcq', 'What is the resultant of 5 N east and 8 N west?', ['13 N east', '3 N west', '3 N east', '13 N west'], 1),
                    ('mcq', 'What is the bearing of due south?', ['270°', '090°', '180°', '000°'], 2),
                ],
                'homework': {
                    'title': 'Vectors in one dimension',
                    'instructions': 'Answer in your workbook with neat diagrams.',
                    'tasks': [
                        'A boat moves at 6 m/s east relative to the water and the river flows at 2 m/s west. Find the resultant velocity.',
                        'Explain the difference between distance and displacement using your route from home to school.',
                        'Draw a scale diagram of a 30 N force on a bearing of 135°.',
                    ],
                    'marks': 10,
                },
            },
            {
                'title': 'Resultant of perpendicular vectors',
                'minutes': 55,
                'objectives': [
                    'I can add two perpendicular vectors using the head-to-tail and tail-to-tail methods.',
                    'I can calculate the magnitude of the resultant with the theorem of Pythagoras.',
                    'I can calculate the direction of the resultant with trigonometry.',
                ],
                'notes': (
                    "<p>When vectors act at right angles, we cannot simply add their magnitudes.</p>"
                    "<p><strong>Head-to-tail method:</strong> draw the first vector. Draw the second vector starting at the "
                    "<em>head</em> of the first. The resultant is drawn from the <em>tail</em> of the first vector to the "
                    "<em>head</em> of the last one.</p>"
                    "<p><strong>Tail-to-tail (parallelogram) method:</strong> draw both vectors from the same point and "
                    "complete the parallelogram (a rectangle for perpendicular vectors). The diagonal from the common tail is the resultant.</p>"
                    "<p>Because the vectors are perpendicular, the diagram is a right-angled triangle:</p>"
                    "<ul><li><strong>Magnitude:</strong> R² = x² + y² (Pythagoras)</li>"
                    "<li><strong>Direction:</strong> tan θ = opposite / adjacent</li></ul>"
                    "<p>You can also find the resultant by an accurate <strong>scale drawing</strong>: measure the length of the "
                    "resultant and its angle with a protractor.</p>"
                    "<p>The resultant of two vectors is largest when they point in the same direction and smallest when they point "
                    "in opposite directions. For 6 N and 8 N it lies between 2 N and 14 N.</p>"
                ),
                'key_terms': [
                    ('head-to-tail method', 'place vectors one after another; the resultant joins the first tail to the last head'),
                    ('tail-to-tail method', 'draw vectors from one point and complete the parallelogram; the diagonal is the resultant'),
                    ('perpendicular', 'at 90° to each other'),
                ],
                'example': {
                    'title': 'Worked example: 6 N east and 8 N north',
                    'html': (
                        "<p><strong>Magnitude:</strong> R² = 6² + 8² = 36 + 64 = 100, so R = <strong>10 N</strong>.</p>"
                        "<p><strong>Direction:</strong> tan θ = 8/6, so θ = 53,1° (measured from east towards north).</p>"
                        "<p><strong>Resultant: 10 N at 53,1° north of east</strong>, which is a bearing of 090° - 53,1° = <strong>036,9°</strong>.</p>"
                        "<p>Always draw a sketch first and mark the angle you are calculating.</p>"
                    ),
                },
                'video': {'id': 'dNMkgsXgtfc', 'title': 'Grade 11 Head to tail vector diagrams',
                          'channel': 'Miss Martins Maths and Science', 'minutes': 12},
                'worksheet': {
                    'instructions': 'Draw a sketch for each question. Give magnitude and direction.',
                    'exercises': [
                        '1. Find the resultant of 3 N east and 4 N north.',
                        '2. Find the resultant of 12 m south and 5 m west.',
                        '3. A plane flies at 200 km/h north and the wind blows at 50 km/h east. Find the resultant velocity.',
                        '4. A learner walks 300 m west and then 400 m south. Find her displacement as a bearing.',
                        '5. Use the tail-to-tail method to draw the resultant of 20 N east and 15 N north to scale (1 cm = 5 N).',
                        '6. Two forces of 9 N and 12 N act on an object. What are the largest and smallest possible resultants?',
                    ],
                },
                'quiz': [
                    ('mcq', 'What is the magnitude of the resultant of 3 N and 4 N acting at 90° to each other?', ['7 N', '1 N', '5 N', '12 N'], 2),
                    ('tf', 'In the head-to-tail method, the resultant is drawn from the tail of the first vector to the head of the last vector.', True),
                    ('mcq', 'A boy walks 5 m north and then 12 m east. What is the magnitude of his displacement?', ['17 m', '13 m', '7 m', '60 m'], 1),
                    ('mcq', 'What is the largest possible resultant of a 6 N and an 8 N force?', ['14 N', '10 N', '2 N', '48 N'], 0),
                ],
                'homework': {
                    'title': 'Perpendicular vectors',
                    'instructions': 'Show sketches and all calculations.',
                    'tasks': [
                        'A swimmer swims at 1,5 m/s across a river (north) that flows at 2,0 m/s east. Find her resultant velocity.',
                        'Find the resultant of 24 N west and 7 N north.',
                        'Check one of your answers with an accurate scale drawing.',
                    ],
                    'marks': 12,
                },
            },
            {
                'title': 'Resolving vectors into components',
                'minutes': 55,
                'objectives': [
                    'I can resolve a vector into horizontal and vertical components.',
                    'I can resolve the weight of an object on an inclined plane into parallel and perpendicular components.',
                    'I can use components to find the resultant of several vectors.',
                ],
                'notes': (
                    "<p>Any vector can be replaced by two perpendicular <strong>components</strong> that together have the same "
                    "effect. This is called <strong>resolving</strong> the vector.</p>"
                    "<p>If a force F makes an angle θ with the horizontal:</p>"
                    "<ul><li>Horizontal component: <strong>Fx = F cos θ</strong></li>"
                    "<li>Vertical component: <strong>Fy = F sin θ</strong></li></ul>"
                    "<p>(If the angle is measured from the vertical, the sine and cosine swap.)</p>"
                    "<p><strong>Inclined planes:</strong> for an object on a slope at angle θ, resolve its weight w = mg into</p>"
                    "<ul><li>a component <strong>parallel</strong> to the slope: w sin θ (pulls the object down the slope)</li>"
                    "<li>a component <strong>perpendicular</strong> to the slope: w cos θ (presses the object into the slope)</li></ul>"
                    "<p><strong>Component method for a resultant:</strong> resolve every vector, add all the x-components, add all the "
                    "y-components, then combine the two totals with Pythagoras and tan θ.</p>"
                    "<p>Use g = 9,8 m·s⁻² in calculations.</p>"
                ),
                'key_terms': [
                    ('component', 'one of two perpendicular vectors that together replace a single vector'),
                    ('resolve', 'to split a vector into its components'),
                    ('inclined plane', 'a flat surface tilted at an angle to the horizontal'),
                ],
                'example': {
                    'title': 'Worked examples: components',
                    'html': (
                        "<p><strong>(a)</strong> A 50 N force pulls a trolley at 30° above the horizontal.<br>"
                        "Fx = 50 cos 30° = <strong>43,3 N</strong> (horizontal)<br>"
                        "Fy = 50 sin 30° = <strong>25,0 N</strong> (vertical)</p>"
                        "<p><strong>(b)</strong> A 10 kg box rests on a slope of 25°.<br>"
                        "w = mg = 10 x 9,8 = 98 N<br>"
                        "Parallel component = 98 sin 25° = <strong>41,4 N</strong> down the slope<br>"
                        "Perpendicular component = 98 cos 25° = <strong>88,8 N</strong> into the slope</p>"
                    ),
                },
                'video': {'id': '-GRcFVx3iz4',
                          'title': 'Grade 11 Physics Resolving Vectors into Components Finding the x and y components',
                          'channel': 'Miss Martins Maths and Science', 'minutes': 12},
                'worksheet': {
                    'instructions': 'Draw a sketch for each question. Use g = 9,8 m/s².',
                    'exercises': [
                        '1. Resolve a force of 80 N at 40° above the horizontal into horizontal and vertical components.',
                        '2. A child pulls a sled with a rope at 35° to the ground with a force of 60 N. What force pulls the sled forward?',
                        '3. A 5 kg block is on a 30° slope. Calculate the components of its weight parallel and perpendicular to the slope.',
                        '4. A velocity of 20 m/s on a bearing of 060°: find its east and north components.',
                        '5. Forces: 10 N east, 6 N north and 4 N west. Find the resultant using components.',
                        '6. The components of a force are 12 N (x) and 5 N (y). Find the force.',
                    ],
                },
                'quiz': [
                    ('mcq', 'What is the horizontal component of a 20 N force at 60° to the horizontal?', ['10 N', '17,3 N', '20 N', '34,6 N'], 0),
                    ('tf', 'If θ is measured from the horizontal, the vertical component of a force F is F sin θ.', True),
                    ('mcq', 'For an object on a slope of angle θ, which component of the weight acts parallel to the slope?', ['mg cos θ', 'mg sin θ', 'mg tan θ', 'mg'], 1),
                    ('mcq', 'A force has components 12 N (x) and 5 N (y). What is its magnitude?', ['17 N', '7 N', '13 N', '60 N'], 2),
                ],
                'homework': {
                    'title': 'Resolving vectors',
                    'instructions': 'Show sketches and all working.',
                    'tasks': [
                        'A 70 N force is applied to a lawnmower handle at 45° below the horizontal. Find the horizontal and vertical components.',
                        'A 12 kg crate is on a ramp inclined at 20°. Calculate the parallel and perpendicular components of its weight.',
                        'Explain why it is easier to push a crate up a gentle slope than a steep slope.',
                    ],
                    'marks': 12,
                },
            },
        ],
    },

    (12, 'PHYS-SCI'): {
        'topic': 'Mechanics: momentum and impulse',
        'caps': 'Mechanics: Momentum and impulse - momentum as a vector (p = mv); change in momentum; '
                "Newton's second law in terms of momentum; impulse (F(net) x Δt = Δp) and its applications "
                'to safety; conservation of linear momentum in an isolated system; elastic and inelastic collisions',
        'summary': 'We define momentum and change in momentum, link force to the rate of change of momentum '
                   'through impulse, and apply the principle of conservation of linear momentum.',
        'days': [
            {
                'title': 'Momentum and change in momentum',
                'minutes': 50,
                'objectives': [
                    'I can define momentum and calculate it with p = mv.',
                    'I can explain why momentum is a vector and use a sign convention.',
                    'I can calculate the change in momentum, including for an object that rebounds.',
                ],
                'notes': (
                    "<p><strong>Momentum</strong> is the product of an object's mass and its velocity:</p>"
                    "<p><strong>p = mv</strong> (unit: kg·m·s⁻¹)</p>"
                    "<p>Momentum is a <strong>vector</strong> with the same direction as the velocity. A truck and a car moving at "
                    "the same speed do not have the same momentum: the more massive truck has more momentum and is harder to stop.</p>"
                    "<p><strong>Change in momentum:</strong> Δp = p(final) - p(initial) = m v(f) - m v(i)</p>"
                    "<p>Because momentum is a vector, choose a <strong>positive direction</strong> first and give velocities in the "
                    "opposite direction a negative sign. This matters most when an object <strong>rebounds</strong>: the change in "
                    "momentum is then larger than either momentum on its own.</p>"
                    "<p>A sketch of the 'before' and 'after' situation helps you get the signs right. Always state the direction "
                    "of your final answer in words, e.g. '5,25 kg·m·s⁻¹ away from the wall'.</p>"
                ),
                'key_terms': [
                    ('momentum', 'the product of the mass and velocity of an object (p = mv)'),
                    ('change in momentum', 'final momentum minus initial momentum (Δp)'),
                    ('sign convention', 'choosing one direction as positive and the opposite as negative'),
                ],
                'example': {
                    'title': 'Worked example: a ball hits a wall',
                    'html': (
                        "<p>A 0,15 kg ball moves at 20 m·s⁻¹ towards a wall and rebounds at 15 m·s⁻¹.</p>"
                        "<p>Take <strong>towards the wall as positive</strong>.</p>"
                        "<p>Δp = m(v(f) - v(i)) = 0,15(-15 - 20) = 0,15 x (-35) = -5,25 kg·m·s⁻¹</p>"
                        "<p><strong>Δp = 5,25 kg·m·s⁻¹ away from the wall.</strong></p>"
                        "<p>Compare: a 1 200 kg car moving at 25 m·s⁻¹ east has p = 1 200 x 25 = <strong>30 000 kg·m·s⁻¹ east</strong>.</p>"
                    ),
                },
                'video': {'id': 'JgM6w4MaO50', 'title': 'Grade 12 Momentum and change in momentum',
                          'channel': 'Miss Martins Maths and Science', 'minutes': 15},
                'worksheet': {
                    'instructions': 'Use a sign convention in every question and give directions.',
                    'exercises': [
                        '1. Define momentum in words.',
                        '2. Calculate the momentum of a 70 kg runner moving at 8 m/s north.',
                        '3. A 2 000 kg truck moves at 15 m/s. Calculate its momentum.',
                        '4. A 0,4 kg ball moving at 10 m/s east is stopped by a goalkeeper. Find the change in momentum.',
                        '5. A 0,06 kg tennis ball hits a racquet at 30 m/s and returns at 40 m/s. Find the magnitude of the change in momentum.',
                        '6. Which has more momentum: a 0,01 kg bullet at 900 m/s or a 60 kg person walking at 1,5 m/s? Show working.',
                    ],
                },
                'quiz': [
                    ('mcq', 'What is the momentum of a 2 kg object moving at 3 m·s⁻¹?', ['6 kg·m·s⁻¹', '1,5 kg·m·s⁻¹', '5 kg·m·s⁻¹', '9 kg·m·s⁻¹'], 0),
                    ('tf', 'Momentum is a scalar quantity.', False),
                    ('mcq', 'A 0,5 kg ball moving at 4 m·s⁻¹ east hits a wall and rebounds at 4 m·s⁻¹ west. What is the magnitude of its change in momentum?',
                     ['0 kg·m·s⁻¹', '2 kg·m·s⁻¹', '4 kg·m·s⁻¹', '8 kg·m·s⁻¹'], 2),
                    ('mcq', 'What is the SI unit of momentum?', ['N', 'kg·m·s⁻¹', 'J', 'kg·m·s⁻²'], 1),
                ],
                'homework': {
                    'title': 'Momentum calculations',
                    'instructions': 'Show the formula, substitution and answer with units and direction.',
                    'tasks': [
                        'A 1 500 kg car slows down from 30 m/s to 10 m/s east. Calculate its change in momentum.',
                        'A 0,2 kg ball falls onto the floor at 6 m/s and bounces up at 4 m/s. Calculate the change in momentum.',
                        'Explain why a rebounding object has a bigger change in momentum than one that stops.',
                    ],
                    'marks': 10,
                },
            },
            {
                'title': "Newton's second law and impulse",
                'minutes': 55,
                'objectives': [
                    "I can state Newton's second law in terms of momentum.",
                    'I can define impulse and use F(net) x Δt = Δp.',
                    'I can explain how safety devices reduce force by increasing contact time.',
                ],
                'notes': (
                    "<p><strong>Newton's second law in terms of momentum:</strong> the net (or resultant) force acting on an object "
                    "is equal to the rate of change of momentum of the object, in the direction of the net force.</p>"
                    "<p><strong>F(net) = Δp / Δt</strong></p>"
                    "<p>Rearranging gives the <strong>impulse</strong>: the product of the net force and the time for which it acts.</p>"
                    "<p><strong>Impulse = F(net) x Δt = Δp</strong> (unit: N·s, which is equal to kg·m·s⁻¹)</p>"
                    "<p>On a force-time graph, the <strong>area under the graph</strong> is the impulse.</p>"
                    "<p><strong>Safety applications:</strong> in a collision, the change in momentum of a passenger is fixed by the "
                    "mass and the change in velocity. If the stopping time Δt is <strong>increased</strong>, the force F = Δp / Δt is "
                    "<strong>smaller</strong>. This is why we use:</p>"
                    "<ul><li>airbags and seatbelts (stretch slightly)</li>"
                    "<li>crumple zones in cars</li>"
                    "<li>helmets with padding, arrestor beds on mountain passes, and bending your knees when you land.</li></ul>"
                ),
                'key_terms': [
                    ('impulse', 'the product of the net force and the time it acts; equal to the change in momentum'),
                    ('net force', 'the resultant of all forces acting on an object'),
                    ('crumple zone', 'part of a car designed to deform and increase collision time'),
                ],
                'example': {
                    'title': 'Worked example: why airbags help',
                    'html': (
                        "<p>A 70 kg passenger moving at 20 m·s⁻¹ is brought to rest in a crash. Take the direction of motion as positive.</p>"
                        "<p>Δp = m(v(f) - v(i)) = 70(0 - 20) = -1 400 kg·m·s⁻¹</p>"
                        "<ul><li>Stopped by the dashboard in 0,02 s: F = Δp / Δt = -1 400 / 0,02 = -70 000 N</li>"
                        "<li>Stopped by an airbag in 0,2 s: F = -1 400 / 0,2 = -7 000 N</li></ul>"
                        "<p>The change in momentum is the same, but the airbag increases the time ten times, so the force on the "
                        "passenger is <strong>ten times smaller</strong> (7 000 N opposite to the motion).</p>"
                    ),
                },
                'video': {'id': 'Foi4zeWJTcs', 'title': '6) Impulse gr 12 | Intro part 1',
                          'channel': 'Kevinmathscience', 'minutes': 8},
                'worksheet': {
                    'instructions': 'Use a sign convention and give units and directions.',
                    'exercises': [
                        "1. State Newton's second law of motion in terms of momentum.",
                        '2. A force of 500 N acts on a ball for 0,02 s. Calculate the impulse.',
                        '3. A 0,45 kg soccer ball is kicked from rest to 25 m/s. Calculate the impulse.',
                        '4. If the foot is in contact with the ball in question 3 for 0,01 s, calculate the average force.',
                        '5. A 1 200 kg car moving at 15 m/s hits a wall and stops in 0,15 s. Calculate the average force on the car.',
                        '6. Explain, using the impulse equation, why bending your knees reduces injury when you jump down.',
                    ],
                },
                'quiz': [
                    ('mcq', 'A force of 500 N acts for 0,02 s. What is the impulse?', ['25 000 N·s', '10 N·s', '520 N·s', '0,00004 N·s'], 1),
                    ('tf', "An airbag reduces the passenger's change in momentum during a collision.", False),
                    ('mcq', 'Why does an airbag reduce the force on a passenger?', ['It reduces the change in momentum', 'It increases the contact time', 'It increases the mass of the passenger'], 1),
                    ('mcq', 'Impulse is equal to the...', ['change in momentum', 'change in kinetic energy', 'mass times acceleration', 'work done'], 0),
                ],
                'homework': {
                    'title': 'Impulse and safety',
                    'instructions': 'Answer in full sentences where explanations are needed.',
                    'tasks': [
                        'A 0,16 kg cricket ball moving at 30 m/s is caught and stopped in 0,1 s. Calculate the average force on the ball.',
                        'Repeat the calculation if the fielder pulls the hands back so that the ball stops in 0,4 s. Comment on the answers.',
                        'Describe two safety features of modern cars and explain how each uses the impulse-momentum theorem.',
                    ],
                    'marks': 12,
                },
            },
            {
                'title': 'Conservation of linear momentum',
                'minutes': 55,
                'objectives': [
                    'I can state the principle of conservation of linear momentum and define an isolated system.',
                    'I can solve collision and explosion problems in one dimension.',
                    'I can use kinetic energy to decide whether a collision is elastic or inelastic.',
                ],
                'notes': (
                    "<p>An <strong>isolated system</strong> is one on which the net external force is zero (friction and other "
                    "outside forces are ignored or balanced).</p>"
                    "<p><strong>Principle of conservation of linear momentum:</strong> the total linear momentum of an isolated "
                    "system remains constant (is conserved).</p>"
                    "<p><strong>Σp(before) = Σp(after)</strong>: m1 v1i + m2 v2i = m1 v1f + m2 v2f</p>"
                    "<p>If the objects stick together after the collision, they share one final velocity: (m1 + m2) vf.</p>"
                    "<p><strong>Explosions</strong> (e.g. a rifle firing, two trolleys pushed apart by a spring) start with total momentum "
                    "zero, so the pieces move off in opposite directions with equal and opposite momenta.</p>"
                    "<p><strong>Elastic or inelastic?</strong> Momentum is conserved in all collisions in an isolated system. Compare "
                    "total kinetic energy (Ek = ½mv²) before and after:</p>"
                    "<ul><li><strong>Elastic:</strong> total Ek is conserved.</li>"
                    "<li><strong>Inelastic:</strong> total Ek is NOT conserved (some is changed into heat, sound and deformation).</li></ul>"
                ),
                'key_terms': [
                    ('isolated system', 'a system on which the net external force is zero'),
                    ('elastic collision', 'a collision in which total kinetic energy is conserved'),
                    ('inelastic collision', 'a collision in which total kinetic energy is not conserved'),
                ],
                'example': {
                    'title': 'Worked examples: collisions and recoil',
                    'html': (
                        "<p><strong>(a) Collision:</strong> trolley A (2 kg) moves right at 3 m·s⁻¹ and collides with trolley B (1 kg) at rest. "
                        "They stick together. Take right as positive.</p>"
                        "<p>Σp(before) = 2(3) + 1(0) = 6 kg·m·s⁻¹ = (2 + 1)vf, so <strong>vf = 2 m·s⁻¹ right</strong>.</p>"
                        "<p>Ek before = ½(2)(3²) = 9 J. Ek after = ½(3)(2²) = 6 J. Ek is not conserved, so the collision is <strong>inelastic</strong>.</p>"
                        "<p><strong>(b) Recoil:</strong> a 4 kg rifle fires a 0,01 kg bullet at 400 m·s⁻¹ forward.<br>"
                        "0 = 0,01(400) + 4v, so v = -1 m·s⁻¹: the rifle recoils at <strong>1 m·s⁻¹ backwards</strong>.</p>"
                    ),
                },
                'video': {'id': 'eieWgUOguU8', 'title': 'Principle of Conservation of linear momentum Grade 12',
                          'channel': 'Miss Martins Maths and Science', 'minutes': 15},
                'worksheet': {
                    'instructions': 'Use a sign convention. Assume all systems are isolated.',
                    'exercises': [
                        '1. State the principle of conservation of linear momentum.',
                        '2. A 1 000 kg car at 20 m/s east hits a stationary 1 500 kg car. They lock together. Find their common velocity.',
                        '3. Is the collision in question 2 elastic or inelastic? Prove it with calculations.',
                        '4. A 60 kg skater at rest pushes off a 40 kg skater. The 40 kg skater moves at 3 m/s west. Find the velocity of the 60 kg skater.',
                        '5. A 3 kg trolley at 4 m/s right collides with a 2 kg trolley at 1 m/s left. Afterwards the 3 kg trolley moves at 1 m/s right. Find the velocity of the 2 kg trolley.',
                        '6. Explain why momentum is not conserved if a large frictional force acts during a collision.',
                    ],
                },
                'quiz': [
                    ('tf', 'In an isolated system, the total linear momentum remains constant.', True),
                    ('mcq', 'A 1 kg trolley at 4 m·s⁻¹ hits a stationary 1 kg trolley and they stick together. What is their common speed?', ['4 m·s⁻¹', '8 m·s⁻¹', '2 m·s⁻¹', '1 m·s⁻¹'], 2),
                    ('mcq', 'What is conserved in an inelastic collision in an isolated system?', ['Both momentum and kinetic energy', 'Only momentum', 'Only kinetic energy', 'Neither'], 1),
                    ('tf', 'In an inelastic collision, total momentum is not conserved.', False),
                ],
                'homework': {
                    'title': 'Conservation of momentum problems',
                    'instructions': 'Show formulae, substitution and answers with directions.',
                    'tasks': [
                        'A 0,02 kg bullet at 300 m/s embeds itself in a 2 kg block at rest on a frictionless surface. Find the velocity of the block and bullet.',
                        'Calculate the kinetic energy lost in the collision above.',
                        'A 50 kg learner jumps forward off a stationary 10 kg skateboard at 2 m/s. Find the velocity of the skateboard.',
                    ],
                    'marks': 15,
                },
            },
        ],
    },

    # =====================================================================
    # LIFE SCIENCES
    # =====================================================================
    (10, 'LIFE-SCI'): {
        'topic': 'Chemistry of life: molecules for life',
        'caps': 'Life at the molecular, cellular and tissue level: Chemistry of life - inorganic compounds '
                '(water, minerals, fertilisers and eutrophication); organic compounds (carbohydrates, '
                'lipids, proteins and enzymes, nucleic acids); vitamins; food tests',
        'summary': 'We study the inorganic and organic molecules that make up living organisms, how '
                   'enzymes work, and how to test foods for nutrients.',
        'days': [
            {
                'title': 'Introduction to the chemistry of life: water and minerals',
                'minutes': 45,
                'objectives': [
                    'I can name the main elements in living organisms and distinguish organic from inorganic compounds.',
                    'I can describe the functions of water in living organisms.',
                    'I can link important minerals to their functions and deficiency diseases, and explain eutrophication.',
                ],
                'notes': (
                    "<p>Living organisms are made mainly of the elements <strong>carbon (C), hydrogen (H), oxygen (O) and "
                    "nitrogen (N)</strong>, with smaller amounts of others such as phosphorus, sulfur, calcium and iron.</p>"
                    "<p><strong>Organic compounds</strong> contain carbon bonded to hydrogen and are made by living things "
                    "(carbohydrates, lipids, proteins, nucleic acids). <strong>Inorganic compounds</strong> generally do not "
                    "contain carbon-hydrogen bonds, e.g. water, minerals and carbon dioxide.</p>"
                    "<p><strong>Water</strong> makes up about 60-70% of the human body. It is a solvent in which reactions take "
                    "place, a transport medium (blood plasma, xylem), a reactant in photosynthesis, and it helps regulate body "
                    "temperature through sweating.</p>"
                    "<p><strong>Minerals</strong> are taken in from food and water (plants absorb them from the soil):</p>"
                    "<ul><li><strong>Calcium:</strong> bones and teeth, blood clotting. Deficiency: weak bones (rickets, osteoporosis).</li>"
                    "<li><strong>Iron:</strong> part of haemoglobin, which carries oxygen. Deficiency: anaemia.</li>"
                    "<li><strong>Iodine:</strong> needed to make the hormone thyroxine. Deficiency: goitre.</li>"
                    "<li><strong>Nitrogen and phosphorus:</strong> needed for proteins, DNA and ATP; important plant nutrients in fertilisers.</li></ul>"
                    "<p>Too much fertiliser washing into rivers and dams causes <strong>eutrophication</strong>: algae grow rapidly, "
                    "die and decompose, oxygen levels drop, and fish and other organisms die.</p>"
                ),
                'key_terms': [
                    ('organic compound', 'a carbon-based compound containing C-H bonds, made by living things'),
                    ('inorganic compound', 'a compound that generally does not contain carbon-hydrogen bonds, e.g. water'),
                    ('mineral', 'an inorganic nutrient needed in small amounts, e.g. iron, calcium'),
                    ('eutrophication', 'excess nutrients in water causing algal bloom and oxygen depletion'),
                ],
                'example': {
                    'title': 'Class activity: mineral match-up',
                    'html': (
                        "<p>In pairs, match each mineral to its function and deficiency, then give one food source.</p>"
                        "<ul><li>Iron: haemoglobin / anaemia / red meat, spinach, beans</li>"
                        "<li>Calcium: bones and teeth / rickets, osteoporosis / milk, cheese, sardines</li>"
                        "<li>Iodine: thyroxine / goitre / iodised salt, seafood</li></ul>"
                        "<p><strong>Discuss:</strong> why do South African regulations require table salt to be iodised? "
                        "(To prevent iodine deficiency and goitre in the population.)</p>"
                    ),
                },
                'video': {'id': 'q4tMUtMRgwM', 'title': 'INTRODUCTION | CHEMISTRY OF LIFE',
                          'channel': 'Miss Angler', 'minutes': 10},
                'worksheet': {
                    'instructions': 'Answer the questions in full sentences.',
                    'exercises': [
                        '1. Name the four elements that make up most of a living organism.',
                        '2. State the difference between an organic and an inorganic compound. Give two examples of each.',
                        '3. List four functions of water in living organisms.',
                        '4. Name the mineral needed for each: (a) haemoglobin (b) strong bones (c) thyroxine.',
                        '5. Name the deficiency disease caused by a lack of iodine.',
                        '6. Describe the steps in eutrophication, starting with fertiliser run-off from a farm.',
                    ],
                },
                'quiz': [
                    ('mcq', 'A lack of iron in the diet causes...', ['goitre', 'anaemia', 'rickets', 'scurvy'], 1),
                    ('tf', 'Water is an organic compound.', False),
                    ('mcq', 'Which mineral is needed to make thyroxine?', ['Calcium', 'Iron', 'Potassium', 'Iodine'], 3),
                    ('mcq', 'Eutrophication of a dam is mainly caused by...', ['excess nutrients from fertilisers', 'a lack of sunlight', 'cold temperatures', 'too many fish'], 0),
                ],
                'homework': {
                    'title': 'Minerals in my diet',
                    'instructions': 'Look at the food you eat at home over one day.',
                    'tasks': [
                        'List the foods you ate and identify one important mineral in at least four of them.',
                        'Explain why a person who eats very little meat or green vegetables may become tired and pale.',
                        'Suggest two ways a farmer can reduce the risk of eutrophication.',
                    ],
                    'marks': 10,
                },
            },
            {
                'title': 'Organic compounds: carbohydrates, lipids, proteins and nucleic acids',
                'minutes': 50,
                'objectives': [
                    'I can describe the elements, building blocks and functions of carbohydrates, lipids and proteins.',
                    'I can name examples of monosaccharides, disaccharides and polysaccharides.',
                    'I can state what nucleic acids are made of and name the two types.',
                ],
                'notes': (
                    "<p>Large organic molecules are built from smaller units (monomers).</p>"
                    "<p><strong>Carbohydrates</strong> (C, H, O) are the main source of energy.</p>"
                    "<ul><li>Monosaccharides (single sugars): glucose, fructose, galactose.</li>"
                    "<li>Disaccharides (two sugars): sucrose (table sugar), maltose, lactose (milk sugar).</li>"
                    "<li>Polysaccharides (many sugars): starch (energy store in plants), glycogen (energy store in animals, in the "
                    "liver and muscles), cellulose (plant cell walls).</li></ul>"
                    "<p><strong>Lipids</strong> (fats and oils; C, H, O) are made of <strong>glycerol and three fatty acids</strong>. "
                    "They store energy, insulate the body and protect organs. Saturated fats (mostly animal fats, solid at room "
                    "temperature) in excess are linked to high cholesterol and heart disease; unsaturated fats (plant oils) are liquid.</p>"
                    "<p><strong>Proteins</strong> (C, H, O, N, sometimes S) are chains of <strong>amino acids</strong> joined by "
                    "peptide bonds. There are 20 different amino acids. Proteins build and repair tissue (muscle, hair), and form "
                    "enzymes, hormones and antibodies. High temperatures or extreme pH <strong>denature</strong> proteins.</p>"
                    "<p><strong>Nucleic acids</strong> (DNA and RNA) are made of <strong>nucleotides</strong>. They carry the genetic "
                    "code and control protein synthesis.</p>"
                ),
                'key_terms': [
                    ('monosaccharide', 'a single sugar unit, e.g. glucose'),
                    ('polysaccharide', 'a large carbohydrate of many sugar units, e.g. starch, glycogen, cellulose'),
                    ('amino acid', 'the building block of proteins'),
                    ('denature', 'to change the shape of a protein permanently so that it no longer works'),
                ],
                'example': {
                    'title': 'Class activity: summary table',
                    'html': (
                        "<p>Complete this table together in class.</p>"
                        "<ul><li><strong>Carbohydrates:</strong> C, H, O / monosaccharides / energy / bread, rice, pap</li>"
                        "<li><strong>Lipids:</strong> C, H, O / glycerol + 3 fatty acids / energy store, insulation / butter, oil, nuts</li>"
                        "<li><strong>Proteins:</strong> C, H, O, N (S) / amino acids / growth, repair, enzymes / eggs, beans, meat</li>"
                        "<li><strong>Nucleic acids:</strong> C, H, O, N, P / nucleotides / genetic information / found in all cells</li></ul>"
                        "<p><strong>Think:</strong> why does a gram of fat release more energy than a gram of carbohydrate? "
                        "(Lipids contain more hydrogen-rich bonds that release energy when broken down: about 38 kJ/g compared with 17 kJ/g.)</p>"
                    ),
                },
                'video': {'id': '1Dx7LDwINLU', 'title': 'Biomolecules (Updated 2023)',
                          'channel': 'Amoeba Sisters', 'minutes': 9},
                'worksheet': {
                    'instructions': 'Answer all questions.',
                    'exercises': [
                        '1. Name the building blocks of: (a) proteins (b) lipids (c) nucleic acids.',
                        '2. Give one example each of a monosaccharide, a disaccharide and a polysaccharide.',
                        '3. Where is glycogen stored in the human body?',
                        '4. Which element is found in proteins but not in carbohydrates or lipids?',
                        '5. Give three functions of proteins.',
                        '6. Explain the difference between saturated and unsaturated fats.',
                        '7. What does it mean if a protein is denatured? Name two things that can denature a protein.',
                    ],
                },
                'quiz': [
                    ('mcq', 'What are the building blocks of proteins?', ['Nucleotides', 'Glucose', 'Amino acids', 'Fatty acids'], 2),
                    ('tf', 'Glycogen is the storage carbohydrate in animals.', True),
                    ('mcq', 'A lipid molecule is made of...', ['glycerol and three fatty acids', 'amino acids', 'glucose units', 'nucleotides'], 0),
                    ('mcq', 'Which element is found in proteins but not in carbohydrates?', ['Carbon', 'Nitrogen', 'Hydrogen', 'Oxygen'], 1),
                ],
                'homework': {
                    'title': 'Read a food label',
                    'instructions': 'Find the nutritional information table on any food package at home.',
                    'tasks': [
                        'Copy the amounts of carbohydrate, total fat, saturated fat and protein per 100 g.',
                        'Which nutrient is present in the largest amount? What is its main function in the body?',
                        'Would you recommend this food for an athlete? Give a reason.',
                    ],
                    'marks': 10,
                },
            },
            {
                'title': 'Enzymes, vitamins and food tests',
                'minutes': 50,
                'objectives': [
                    'I can explain how enzymes work using the lock-and-key model and the effect of temperature and pH.',
                    'I can link vitamins A, C and D to their functions and deficiency diseases.',
                    'I can describe food tests for starch, glucose, protein and fats.',
                ],
                'notes': (
                    "<p><strong>Enzymes</strong> are proteins that act as <strong>biological catalysts</strong>: they speed up chemical "
                    "reactions in cells without being used up.</p>"
                    "<ul><li><strong>Lock-and-key model:</strong> the substrate (key) fits into the enzyme's <strong>active site</strong> (lock). "
                    "Each enzyme is <strong>specific</strong>: it acts on only one type of substrate.</li>"
                    "<li><strong>Temperature:</strong> enzymes work best at an optimum temperature (about 37 °C in humans). Very high "
                    "temperatures <strong>denature</strong> the enzyme: the active site changes shape and no longer fits the substrate. "
                    "Low temperatures slow enzymes down but do not denature them.</li>"
                    "<li><strong>pH:</strong> each enzyme has an optimum pH, e.g. pepsin in the stomach works best in acidic conditions.</li></ul>"
                    "<p><strong>Vitamins</strong> are organic compounds needed in small amounts: vitamin A (vision; deficiency causes night "
                    "blindness), vitamin C (healthy gums and skin; deficiency causes scurvy), vitamin D (absorbing calcium; deficiency causes rickets).</p>"
                    "<p><strong>Food tests:</strong></p>"
                    "<ul><li>Starch: iodine solution turns from yellow-brown to <strong>blue-black</strong>.</li>"
                    "<li>Glucose (reducing sugar): heat with Benedict's solution; blue turns <strong>orange / brick-red</strong>.</li>"
                    "<li>Protein: Biuret reagent turns from blue to <strong>purple / violet</strong>.</li>"
                    "<li>Fats: rub on brown paper; a <strong>translucent</strong> spot remains.</li></ul>"
                ),
                'key_terms': [
                    ('enzyme', 'a protein that speeds up a chemical reaction in a cell'),
                    ('active site', 'the part of an enzyme where the substrate binds'),
                    ('substrate', 'the substance an enzyme acts on'),
                    ('optimum', 'the condition (temperature or pH) at which an enzyme works best'),
                ],
                'example': {
                    'title': 'Practical: testing foods',
                    'html': (
                        "<p><strong>Aim:</strong> to test bread, egg white, a glucose solution and cooking oil for nutrients.</p>"
                        "<ol><li>Add a few drops of iodine to bread: blue-black means <strong>starch is present</strong>.</li>"
                        "<li>Add Benedict's solution to the glucose solution and heat in a water bath for 3-5 minutes: orange/brick-red means <strong>glucose is present</strong>.</li>"
                        "<li>Add Biuret reagent to egg white: purple means <strong>protein is present</strong>.</li>"
                        "<li>Rub oil on brown paper and hold it up to the light: a translucent spot means <strong>fat is present</strong>.</li></ol>"
                        "<p><strong>Safety:</strong> wear safety glasses, use a water bath (not a direct flame) and point test tubes away from people.</p>"
                    ),
                },
                'video': {'id': 'sWD9UhzbCJE', 'title': 'Life Sciences Grade 10 | Food Tests: Proteins and Glucose (CAPS)',
                          'channel': 'Ace My Exams ', 'minutes': 10},
                'worksheet': {
                    'instructions': 'Answer the questions. Use the notes and the practical.',
                    'exercises': [
                        '1. Define the term enzyme.',
                        '2. Use the lock-and-key model to explain why enzymes are specific.',
                        '3. Explain why an enzyme stops working at 70 °C.',
                        '4. Name the reagent and the positive colour change for: (a) starch (b) glucose (c) protein.',
                        '5. A learner adds iodine to a potato slice and it turns blue-black. What does this show?',
                        '6. Name the vitamin whose deficiency causes: (a) scurvy (b) rickets (c) night blindness.',
                    ],
                },
                'quiz': [
                    ('mcq', 'What colour does iodine solution turn in the presence of starch?', ['Orange', 'Blue-black', 'Purple', 'Green'], 1),
                    ('tf', 'Enzymes are denatured by very high temperatures.', True),
                    ('mcq', "What is a positive result for glucose with Benedict's solution after heating?", ['Blue-black', 'Purple', 'Orange / brick-red', 'Colourless'], 2),
                    ('mcq', 'A lack of vitamin C causes...', ['scurvy', 'rickets', 'night blindness', 'goitre'], 0),
                    ('mcq', "In the lock-and-key model, the 'lock' is...", ['the substrate', 'the product', "the enzyme's active site"], 2),
                ],
                'homework': {
                    'title': 'Enzymes in daily life',
                    'instructions': 'Answer in your workbook.',
                    'tasks': [
                        'Explain why biological washing powders (which contain enzymes) work poorly in very hot water.',
                        'Draw and label a simple diagram of the lock-and-key model.',
                        'Plan a simple fair test to find out whether milk contains protein. Name the reagent and the expected result.',
                    ],
                    'marks': 12,
                },
            },
        ],
    },

    (11, 'LIFE-SCI'): {
        'topic': 'Biodiversity and classification of micro-organisms',
        'caps': 'Diversity, change and continuity: Biodiversity and classification of micro-organisms - '
                'general structure, characteristics, ecological and economic role, and diseases of viruses, '
                'bacteria, protists and fungi; immunity; medicines and biotechnology',
        'summary': 'We study the four groups of micro-organisms (viruses, bacteria, protists and fungi): '
                   'their structure, the diseases they cause and their useful roles.',
        'days': [
            {
                'title': 'Micro-organisms and viruses',
                'minutes': 50,
                'objectives': [
                    'I can name the four groups of micro-organisms.',
                    'I can describe the structure of a virus and explain why viruses are not considered fully alive.',
                    'I can describe how HIV affects the body and how viral diseases are treated or prevented.',
                ],
                'notes': (
                    "<p><strong>Micro-organisms</strong> are organisms too small to be seen with the naked eye. The four groups are "
                    "<strong>viruses, bacteria, protists and fungi</strong>. Most are harmless or useful; some cause disease and are "
                    "called <strong>pathogens</strong>.</p>"
                    "<p><strong>Viruses</strong> are the smallest. They are not made of cells:</p>"
                    "<ul><li>A protein coat called a <strong>capsid</strong> surrounds genetic material (DNA <em>or</em> RNA).</li>"
                    "<li>Some have an outer envelope.</li>"
                    "<li>They have no cytoplasm, no organelles and no metabolism.</li></ul>"
                    "<p>Viruses can only reproduce <strong>inside a living host cell</strong>: they inject their genetic material, take "
                    "over the cell to make new viruses, and the cell bursts. Outside a cell they can crystallise. This is why many "
                    "biologists say viruses are on the border between living and non-living.</p>"
                    "<p><strong>Viral diseases</strong> include influenza, measles, rabies, the common cold and HIV/AIDS. "
                    "<strong>HIV</strong> attacks T-helper (CD4) lymphocytes, weakening the immune system so that other infections "
                    "(e.g. TB) develop. <strong>Antiretroviral drugs (ARVs)</strong> slow the virus down.</p>"
                    "<p><strong>Antibiotics do not work against viruses.</strong> Vaccines help prevent viral diseases such as measles and polio.</p>"
                ),
                'key_terms': [
                    ('pathogen', 'a micro-organism that causes disease'),
                    ('capsid', 'the protein coat of a virus'),
                    ('host cell', 'a living cell that a virus infects and uses to reproduce'),
                    ('vaccine', 'a weakened or inactive form of a pathogen that trains the immune system'),
                ],
                'example': {
                    'title': 'Class debate: is a virus alive?',
                    'html': (
                        "<p>Draw two columns: <strong>characteristics of life</strong> and <strong>do viruses show them?</strong></p>"
                        "<ul><li>Made of cells: no</li>"
                        "<li>Nutrition and respiration: no</li>"
                        "<li>Reproduction: yes, but only inside a host cell</li>"
                        "<li>Contain genetic material (DNA or RNA): yes</li>"
                        "<li>Can change (mutate) over time: yes</li></ul>"
                        "<p><strong>Conclusion:</strong> viruses show some characteristics of life only when inside a host cell, so they "
                        "are often described as being between living and non-living.</p>"
                    ),
                },
                'video': {'id': 'waylMQhMACw', 'title': 'Biodiversity and Classification of Micro-organisms : Grade 11 Life Sciences',
                          'channel': 'Mindset', 'minutes': 25},
                'worksheet': {
                    'instructions': 'Answer the questions in full sentences.',
                    'exercises': [
                        '1. Name the four groups of micro-organisms.',
                        '2. Draw and label the basic structure of a virus.',
                        '3. Give two reasons why viruses are not considered to be fully living.',
                        '4. Explain why a doctor will not prescribe antibiotics for flu.',
                        '5. Which cells in the body does HIV attack? Explain how this leads to AIDS.',
                        '6. Name three diseases caused by viruses.',
                    ],
                },
                'quiz': [
                    ('tf', 'Antibiotics are effective against viruses.', False),
                    ('mcq', 'What is the protein coat of a virus called?', ['Cell wall', 'Capsid', 'Nucleus', 'Capsule'], 1),
                    ('mcq', 'Which cells does HIV attack?', ['Red blood cells', 'Nerve cells', 'T-helper (CD4) cells', 'Liver cells'], 2),
                    ('mcq', 'Where can viruses reproduce?', ['Only inside living host cells', 'In soil by binary fission', 'In the air by spores'], 0),
                ],
                'homework': {
                    'title': 'Viruses and society',
                    'instructions': 'Use your notes and the textbook.',
                    'tasks': [
                        'Write a short paragraph (8-10 lines) on how HIV is transmitted and how its spread can be reduced.',
                        'Explain how a vaccine helps protect a person against a viral disease.',
                    ],
                    'marks': 10,
                },
            },
            {
                'title': 'Bacteria',
                'minutes': 50,
                'objectives': [
                    'I can describe and label the structure of a bacterial cell.',
                    'I can describe how bacteria reproduce and name the three main shapes.',
                    'I can explain the useful roles of bacteria and name bacterial diseases.',
                ],
                'notes': (
                    "<p><strong>Bacteria</strong> are single-celled <strong>prokaryotes</strong>: they have no true nucleus and no "
                    "membrane-bound organelles.</p>"
                    "<p><strong>Structure:</strong> cell wall, cell membrane, cytoplasm, a single circular chromosome (DNA) in the "
                    "cytoplasm, small rings of DNA called <strong>plasmids</strong>, ribosomes, and in some species a slime "
                    "<strong>capsule</strong> and a whip-like <strong>flagellum</strong> for movement.</p>"
                    "<p><strong>Shapes:</strong> cocci (spherical), bacilli (rod-shaped) and spirilla (spiral).</p>"
                    "<p><strong>Reproduction:</strong> asexually by <strong>binary fission</strong>: the cell copies its DNA and divides "
                    "into two. In good conditions this can happen every 20 minutes, so numbers grow very quickly.</p>"
                    "<p><strong>Useful roles:</strong></p>"
                    "<ul><li>Decomposers recycle nutrients in ecosystems.</li>"
                    "<li>Nitrogen-fixing bacteria in the root nodules of legumes (beans, peas) add nitrogen to the soil.</li>"
                    "<li>Making yoghurt, cheese and amasi; genetically modified bacteria produce human insulin.</li>"
                    "<li>Gut bacteria help digestion and make vitamin K.</li></ul>"
                    "<p><strong>Diseases:</strong> tuberculosis (TB), cholera, typhoid. They are treated with <strong>antibiotics</strong>. "
                    "Misuse of antibiotics (e.g. not finishing a course) leads to <strong>antibiotic resistance</strong>.</p>"
                ),
                'key_terms': [
                    ('prokaryote', 'an organism whose cells have no true nucleus'),
                    ('binary fission', 'asexual reproduction in which one cell divides into two identical cells'),
                    ('plasmid', 'a small ring of DNA in a bacterial cell'),
                    ('antibiotic resistance', 'when bacteria are no longer killed by an antibiotic'),
                ],
                'example': {
                    'title': 'Worked example: bacterial growth',
                    'html': (
                        "<p>One bacterium divides by binary fission every 20 minutes. How many bacteria are there after 2 hours?</p>"
                        "<ul><li>2 hours = 120 minutes = 120 ÷ 20 = 6 divisions</li>"
                        "<li>Each division doubles the number: 1 x 2^6</li>"
                        "<li><strong>64 bacteria</strong></li></ul>"
                        "<p>After 4 hours (12 divisions) there would be 2^12 = 4 096. This is why food left out of the fridge spoils "
                        "quickly and why a wound infection can spread fast.</p>"
                    ),
                },
                'video': {'id': 'gcvYmyyMqHI', 'title': 'Bacteria - Grade 11 Life Sciences',
                          'channel': 'Edu-ca-te', 'minutes': 10},
                'worksheet': {
                    'instructions': 'Answer all questions.',
                    'exercises': [
                        '1. Draw and label a bacterial cell (at least six labels).',
                        '2. State two structural differences between a bacterial cell and an animal cell.',
                        '3. Name and describe the three shapes of bacteria.',
                        '4. A bacterium divides every 30 minutes. How many bacteria will there be after 3 hours, starting with one?',
                        '5. Explain the role of nitrogen-fixing bacteria.',
                        '6. Name two diseases caused by bacteria and how they are treated.',
                        '7. Explain why it is important to finish a full course of antibiotics.',
                    ],
                },
                'quiz': [
                    ('mcq', 'How do bacteria reproduce?', ['Binary fission', 'Spores only', 'Meiosis', 'Budding from a nucleus'], 0),
                    ('tf', 'Bacteria have a true nucleus.', False),
                    ('mcq', 'What are rod-shaped bacteria called?', ['Cocci', 'Bacilli', 'Spirilla'], 1),
                    ('mcq', 'Tuberculosis (TB) is caused by a...', ['virus', 'protist', 'bacterium', 'fungus'], 2),
                ],
                'homework': {
                    'title': 'Useful and harmful bacteria',
                    'instructions': 'Make a two-column table.',
                    'tasks': [
                        'List four useful roles of bacteria and four harmful effects.',
                        'Explain how amasi or yoghurt is made with the help of bacteria.',
                    ],
                    'marks': 10,
                },
            },
            {
                'title': 'Protists and fungi',
                'minutes': 50,
                'objectives': [
                    'I can describe the general characteristics of protists and fungi.',
                    'I can explain how malaria is caused and spread.',
                    'I can describe useful and harmful roles of fungi.',
                ],
                'notes': (
                    "<p><strong>Protists</strong> are <strong>eukaryotes</strong> (cells with a true nucleus) that are mostly "
                    "single-celled. They live in water or moist places. Examples: Amoeba, Paramecium, many algae (which "
                    "photosynthesise and produce much of the world's oxygen) and Plasmodium.</p>"
                    "<p><strong>Malaria</strong> is caused by the protist <strong>Plasmodium</strong>. It is spread by the bite of an "
                    "infected <strong>female Anopheles mosquito</strong>, which is the <em>vector</em>. Plasmodium multiplies in the liver "
                    "and red blood cells, causing fever and chills. In South Africa malaria occurs mainly in parts of Limpopo, "
                    "Mpumalanga and northern KwaZulu-Natal. Prevention: mosquito nets, insect repellent, spraying and "
                    "anti-malaria medication.</p>"
                    "<p><strong>Fungi</strong> are eukaryotes with cell walls made of <strong>chitin</strong>. They cannot photosynthesise: "
                    "they are heterotrophs that feed by secreting enzymes onto food and absorbing it (saprophytes) or by living on a "
                    "host (parasites). Most consist of threads called <strong>hyphae</strong> that form a <strong>mycelium</strong>, and they "
                    "reproduce by <strong>spores</strong>. Yeast is a single-celled fungus.</p>"
                    "<ul><li><strong>Useful:</strong> decomposers; yeast for bread and fermentation; Penicillium mould produces the antibiotic "
                    "penicillin; edible mushrooms.</li>"
                    "<li><strong>Harmful:</strong> thrush (Candida), ringworm and athlete's foot; food spoilage; crop diseases such as rust.</li></ul>"
                ),
                'key_terms': [
                    ('eukaryote', 'an organism whose cells have a true nucleus'),
                    ('vector', 'an organism that carries a pathogen from one host to another'),
                    ('hyphae', 'thread-like filaments that make up the body of most fungi'),
                    ('saprophyte', 'an organism that feeds on dead and decaying matter'),
                ],
                'example': {
                    'title': 'Class activity: compare the four groups',
                    'html': (
                        "<ul><li><strong>Viruses:</strong> not cells; DNA or RNA in a capsid; e.g. HIV, influenza</li>"
                        "<li><strong>Bacteria:</strong> prokaryotic cells; cell wall; binary fission; e.g. TB, cholera</li>"
                        "<li><strong>Protists:</strong> eukaryotic, mostly unicellular; e.g. Amoeba, Plasmodium (malaria)</li>"
                        "<li><strong>Fungi:</strong> eukaryotic; chitin cell walls; hyphae and spores; e.g. yeast, Penicillium, Candida (thrush)</li></ul>"
                        "<p><strong>Mini-investigation:</strong> leave a slice of moist bread in a sealed bag for a week and observe the mould "
                        "(do not open the bag; dispose of it safely).</p>"
                    ),
                },
                'video': {'id': 'zK7Ckmxxqds', 'title': 'Protists and Fungi',
                          'channel': 'Amoeba Sisters', 'minutes': 8},
                'worksheet': {
                    'instructions': 'Answer all questions.',
                    'exercises': [
                        '1. Give two characteristics of protists.',
                        '2. Name the organism that causes malaria and the vector that spreads it.',
                        '3. Suggest three ways to prevent malaria.',
                        '4. What substance makes up the cell walls of fungi?',
                        '5. Explain how a saprophytic fungus obtains its food.',
                        '6. Give two economic uses and two diseases of fungi.',
                        '7. Complete a table comparing viruses, bacteria, protists and fungi (cell type, example, one disease).',
                    ],
                },
                'quiz': [
                    ('mcq', 'What causes malaria?', ['A virus', 'A bacterium', 'Plasmodium (a protist)', 'Yeast'], 2),
                    ('tf', 'Fungal cell walls contain chitin.', True),
                    ('mcq', 'Which organism is the vector of malaria?', ['Housefly', 'Female Anopheles mosquito', 'Tsetse fly', 'Male Anopheles mosquito'], 1),
                    ('mcq', 'The antibiotic penicillin was first obtained from...', ['yeast', 'Plasmodium', 'a virus', 'Penicillium mould'], 3),
                ],
                'homework': {
                    'title': 'Micro-organisms summary',
                    'instructions': 'Create a one-page mind map of the four groups of micro-organisms.',
                    'tasks': [
                        'For each group include: structure, how it reproduces, one useful role (if any) and one disease.',
                        'Add one prevention method for a disease from each group.',
                    ],
                    'marks': 15,
                },
            },
        ],
    },

    (12, 'LIFE-SCI'): {
        'topic': 'DNA: the code of life',
        'caps': 'Life at the molecular, cellular and tissue level: DNA - the code of life: nucleic acids; '
                'location, structure and functions of DNA; discovery of the DNA structure (Watson, Crick, '
                'Franklin, Wilkins); DNA replication; DNA profiling; (followed by RNA and protein synthesis)',
        'summary': 'We study the structure and location of DNA, how DNA replicates, and how DNA '
                   'profiling is used.',
        'days': [
            {
                'title': 'Location and structure of DNA',
                'minutes': 50,
                'objectives': [
                    'I can state where DNA is found in a cell.',
                    'I can describe the structure of a nucleotide and of the DNA double helix.',
                    'I can apply the base-pairing rule and describe the scientists who discovered the structure of DNA.',
                ],
                'notes': (
                    "<p>Nucleic acids are DNA (deoxyribonucleic acid) and RNA (ribonucleic acid).</p>"
                    "<p><strong>Location of DNA:</strong> most DNA is in the <strong>nucleus</strong>, where it forms chromosomes "
                    "(nuclear DNA). Small amounts are found in <strong>mitochondria</strong> and, in plants, in "
                    "<strong>chloroplasts</strong> (extra-nuclear DNA).</p>"
                    "<p><strong>Structure:</strong> DNA is a polymer of <strong>nucleotides</strong>. Each nucleotide consists of</p>"
                    "<ul><li>a deoxyribose sugar</li><li>a phosphate group</li>"
                    "<li>a nitrogenous base: adenine (A), thymine (T), guanine (G) or cytosine (C).</li></ul>"
                    "<p>DNA is a <strong>double helix</strong>: two strands twisted like a spiral ladder. The sides of the ladder are "
                    "alternating sugar and phosphate; the rungs are pairs of bases held together by weak <strong>hydrogen bonds</strong>. "
                    "Bases pair in a fixed way (complementary base pairing): <strong>A with T</strong> and <strong>G with C</strong>.</p>"
                    "<p>A <strong>gene</strong> is a segment of DNA that codes for a particular protein (and so a characteristic).</p>"
                    "<p><strong>History:</strong> in 1953 James Watson and Francis Crick proposed the double-helix model, using X-ray "
                    "diffraction images made by Rosalind Franklin and data from Maurice Wilkins.</p>"
                ),
                'key_terms': [
                    ('nucleotide', 'the building block of DNA: a sugar, a phosphate and a nitrogenous base'),
                    ('double helix', 'the shape of DNA: two strands twisted around each other'),
                    ('complementary base pairing', 'A always pairs with T, and G always pairs with C'),
                    ('gene', 'a section of DNA that codes for a protein'),
                ],
                'example': {
                    'title': 'Worked examples: base pairing',
                    'html': (
                        "<p><strong>(a)</strong> One strand reads A T G C C A. The complementary strand is <strong>T A C G G T</strong>.</p>"
                        "<p><strong>(b)</strong> A DNA sample has 30% adenine. Calculate the other bases.</p>"
                        "<ul><li>A pairs with T, so T = 30%.</li>"
                        "<li>A + T = 60%, so G + C = 40%.</li>"
                        "<li>G = C, so G = 20% and C = 20%.</li></ul>"
                    ),
                },
                'video': {'id': '4u8nC8BAq9s', 'title': 'Introduction to DNA structure',
                          'channel': 'Miss Angler', 'minutes': 10},
                'worksheet': {
                    'instructions': 'Answer all questions.',
                    'exercises': [
                        '1. Name three places in a plant cell where DNA is found.',
                        '2. Draw and label a DNA nucleotide.',
                        '3. Write the complementary strand for: G C T A A T C G',
                        '4. A DNA molecule has 18% cytosine. Calculate the percentage of each of the other bases.',
                        '5. What type of bond holds the two strands of DNA together?',
                        '6. Describe the contributions of Watson, Crick, Franklin and Wilkins.',
                        '7. Define a gene.',
                    ],
                },
                'quiz': [
                    ('mcq', 'Which base pairs with adenine in DNA?', ['Uracil', 'Guanine', 'Thymine', 'Cytosine'], 2),
                    ('tf', 'DNA is found in mitochondria as well as in the nucleus.', True),
                    ('mcq', 'If 22% of the bases in a DNA molecule are guanine, what percentage are adenine?', ['22%', '28%', '56%', '44%'], 1),
                    ('mcq', 'What sugar is found in DNA?', ['Ribose', 'Glucose', 'Sucrose', 'Deoxyribose'], 3),
                ],
                'homework': {
                    'title': 'Build a DNA model',
                    'instructions': 'Use paper, sweets, beads or any household materials.',
                    'tasks': [
                        'Make (or draw in colour) a model of a DNA segment with at least 8 base pairs.',
                        'Include a key showing the sugar, phosphate and each of the four bases.',
                        'Write two sentences explaining how your model shows complementary base pairing.',
                    ],
                    'marks': 15,
                },
            },
            {
                'title': 'DNA replication',
                'minutes': 50,
                'objectives': [
                    'I can state when and where DNA replication takes place.',
                    'I can describe the steps of DNA replication.',
                    'I can explain the significance of DNA replication.',
                ],
                'notes': (
                    "<p><strong>DNA replication</strong> is the process by which a DNA molecule makes an identical copy of itself.</p>"
                    "<p><strong>When and where:</strong> during <strong>interphase</strong> of the cell cycle, before a cell divides by "
                    "mitosis or meiosis, in the <strong>nucleus</strong>.</p>"
                    "<p><strong>Steps:</strong></p>"
                    "<ol><li>The double helix <strong>unwinds</strong>.</li>"
                    "<li>The weak <strong>hydrogen bonds</strong> between the bases break (controlled by enzymes) and the two strands "
                    "separate (\"unzip\").</li>"
                    "<li>Each original strand acts as a <strong>template</strong>.</li>"
                    "<li>Free DNA nucleotides in the nucleoplasm attach to the exposed bases according to the base-pairing rule "
                    "(A with T, G with C).</li>"
                    "<li>This forms two identical DNA molecules, each made of <strong>one original strand and one new strand</strong>. "
                    "Each molecule then winds into a double helix.</li></ol>"
                    "<p><strong>Significance:</strong> replication doubles the DNA so that each daughter cell receives an exact copy of "
                    "the genetic information. Mistakes during replication cause <strong>mutations</strong>, which can be harmful, "
                    "neutral or occasionally useful.</p>"
                ),
                'key_terms': [
                    ('DNA replication', 'the process in which DNA makes an identical copy of itself'),
                    ('interphase', 'the phase of the cell cycle between divisions when DNA replicates'),
                    ('template', 'an original strand used as a pattern to build a new strand'),
                    ('mutation', 'a change in the sequence of bases in DNA'),
                ],
                'example': {
                    'title': 'Worked example: following replication',
                    'html': (
                        "<p>A DNA segment has the strands:</p>"
                        "<p>Strand 1: A T G C A G<br>Strand 2: T A C G T C</p>"
                        "<p>After unzipping, free nucleotides pair with each template:</p>"
                        "<ul><li>Strand 1 (A T G C A G) builds a new strand T A C G T C</li>"
                        "<li>Strand 2 (T A C G T C) builds a new strand A T G C A G</li></ul>"
                        "<p>Result: <strong>two identical DNA molecules</strong>, each with one original strand and one new strand.</p>"
                        "<p>If a mistake placed C opposite A, the new molecule would contain a mutation.</p>"
                    ),
                },
                'video': {'id': 'Qqe4thU-os8', 'title': 'DNA Replication (Updated)',
                          'channel': 'Amoeba Sisters', 'minutes': 9},
                'worksheet': {
                    'instructions': 'Answer all questions.',
                    'exercises': [
                        '1. Define DNA replication.',
                        '2. During which phase of the cell cycle does replication take place?',
                        '3. Describe the process of DNA replication in five steps.',
                        '4. A template strand reads T T A C G G A T. Write the new strand that forms on it.',
                        '5. Why is it important that DNA replicates before cell division?',
                        '6. What is a mutation? How can an error in replication cause one?',
                    ],
                },
                'quiz': [
                    ('mcq', 'When does DNA replication take place?', ['Prophase', 'Interphase', 'Metaphase', 'Telophase'], 1),
                    ('tf', 'Each new DNA molecule formed during replication has one original strand and one new strand.', True),
                    ('mcq', 'Which bonds break when the DNA double helix unzips?', ['Peptide bonds', 'Ionic bonds', 'Hydrogen bonds', 'Glycosidic bonds'], 2),
                    ('mcq', 'A template strand reads T A C G G A. What is the new strand?', ['A T G C C T', 'U A C G G A', 'T A C G G A', 'A U G C C U'], 0),
                ],
                'homework': {
                    'title': 'DNA replication flow diagram',
                    'instructions': 'Use labelled diagrams.',
                    'tasks': [
                        'Draw a flow diagram (at least four stages) showing DNA replication, labelling the original and new strands in different colours.',
                        'Explain in your own words why DNA replication is described as producing two identical copies.',
                    ],
                    'marks': 10,
                },
            },
            {
                'title': 'DNA profiling',
                'minutes': 50,
                'objectives': [
                    'I can define DNA profiling and outline how a DNA profile is made.',
                    'I can describe the uses of DNA profiling.',
                    'I can interpret a simple DNA profile in a paternity or forensic case.',
                ],
                'notes': (
                    "<p>Most of our DNA is the same in all humans, but some regions, especially <strong>non-coding</strong> regions with "
                    "short repeated sequences, vary greatly between people. A <strong>DNA profile</strong> (DNA fingerprint) is the pattern "
                    "of bands produced from these variable regions. Apart from identical twins, every person's profile is unique.</p>"
                    "<p><strong>How a profile is made (outline):</strong></p>"
                    "<ol><li>DNA is extracted from a sample such as blood, saliva, hair roots or skin cells.</li>"
                    "<li>If the sample is small, the DNA is copied many times (PCR).</li>"
                    "<li>Enzymes cut the DNA into fragments.</li>"
                    "<li>The fragments are separated by size using <strong>gel electrophoresis</strong>: smaller fragments travel further.</li>"
                    "<li>The fragments are made visible as a pattern of <strong>bands</strong>.</li></ol>"
                    "<p><strong>Uses:</strong> identifying suspects from crime-scene evidence; proving innocence; paternity and other "
                    "family relationship tests; identifying bodies after disasters; diagnosing some inherited disorders.</p>"
                    "<p><strong>Paternity:</strong> a child inherits half of its DNA from each biological parent, so every band in the "
                    "child's profile must match a band in either the mother or the father.</p>"
                    "<p><strong>Ethical concerns</strong> include privacy, who may keep and use DNA databases, and the risk of samples "
                    "being contaminated or misused.</p>"
                ),
                'key_terms': [
                    ('DNA profile', 'a pattern of DNA bands unique to an individual (except identical twins)'),
                    ('gel electrophoresis', 'a technique that separates DNA fragments according to size'),
                    ('forensic', 'relating to the use of science in investigating crimes'),
                ],
                'example': {
                    'title': 'Worked example: a paternity case',
                    'html': (
                        "<p>A child's profile has bands at positions 2, 4, 6 and 7. The mother's bands are at 2, 5 and 6. "
                        "Two possible fathers have been tested:</p>"
                        "<ul><li>Man X: bands at 1, 4, 7 and 8</li>"
                        "<li>Man Y: bands at 3, 4 and 5</li></ul>"
                        "<p><strong>Step 1:</strong> identify the child's bands that came from the mother: 2 and 6.</p>"
                        "<p><strong>Step 2:</strong> the remaining bands (4 and 7) must come from the father.</p>"
                        "<p><strong>Step 3:</strong> Man X has both 4 and 7; Man Y has 4 but not 7.</p>"
                        "<p><strong>Conclusion: Man X is likely to be the biological father.</strong></p>"
                    ),
                },
                'video': {'id': '32P63Kz75qo', 'title': 'DNA profiling |  Reading DNA profiles',
                          'channel': 'Miss Angler', 'minutes': 10},
                'worksheet': {
                    'instructions': 'Answer all questions.',
                    'exercises': [
                        '1. Define DNA profiling.',
                        '2. Name four sources of DNA that could be collected at a crime scene.',
                        '3. List the main steps in producing a DNA profile.',
                        '4. Why do identical twins have the same DNA profile?',
                        '5. Crime-scene bands: 1, 3, 6. Suspect A: 1, 3, 6. Suspect B: 2, 3, 5. Which suspect matches? Explain.',
                        '6. Give three uses of DNA profiling other than solving crimes.',
                        '7. Discuss one ethical concern about storing DNA profiles in a database.',
                    ],
                },
                'quiz': [
                    ('tf', 'Identical twins have the same DNA profile.', True),
                    ('mcq', 'Which technique separates DNA fragments by size?', ['A centrifuge', 'Gel electrophoresis', 'A light microscope', 'Chromatography paper'], 1),
                    ('mcq', 'Which is NOT a use of DNA profiling?', ['Paternity testing', 'Identifying crime suspects', "Changing a person's eye colour", 'Identifying disaster victims'], 2),
                    ('mcq', "Where do the bands in a child's DNA profile come from?", ['All from the mother', 'All from the father', 'From both biological parents (about half from each)'], 2),
                ],
                'homework': {
                    'title': 'DNA profiling case study',
                    'instructions': 'Write a short report (about one page).',
                    'tasks': [
                        'Describe how DNA profiling could be used to identify victims after a natural disaster.',
                        'Give two arguments for and two arguments against a national DNA database.',
                        'State and justify your own opinion.',
                    ],
                    'marks': 15,
                },
            },
        ],
    },
}
