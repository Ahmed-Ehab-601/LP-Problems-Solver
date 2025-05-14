class SubscriptSuperscriptLists:
    def __init__(self):
        # Unicode for subscript numbers (1 to 20)
        subscript_numbers = {
            1: "\u2081", 2: "\u2082", 3: "\u2083", 4: "\u2084", 5: "\u2085",
            6: "\u2086", 7: "\u2087", 8: "\u2088", 9: "\u2089", 10: "\u2081\u2080",
            11: "\u2081\u2081", 12: "\u2081\u2082", 13: "\u2081\u2083", 14: "\u2081\u2084",
            15: "\u2081\u2085", 16: "\u2081\u2086", 17: "\u2081\u2087", 18: "\u2081\u2088",
            19: "\u2081\u2089", 20: "\u2082\u2080"
        }
       
        # Unicode for superscript + and -
        superscript_plus = "\u207A"
        superscript_minus = "\u207B"

        # Initialize the three lists
        self.slist = [f"s{subscript_numbers[i]}" for i in range(1, 21)]
        self.spluslist = [f"s{subscript_numbers[i]}{superscript_plus}" for i in range(1, 21)]
        self.sminuslist = [f"s{subscript_numbers[i]}{superscript_minus}" for i in range(1, 21)]
        self.plist = [f"p{subscript_numbers[i]}" for i in range(1, 21)]
        self.xpluslist = [f"x{subscript_numbers[i]}{superscript_plus}" for i in range(1, 21)]
        self.xminuslist = [f"x{subscript_numbers[i]}{superscript_minus}" for i in range(1, 21)]
        self.alist = [f"a{subscript_numbers[i]}" for i in range(1, 21)]
        self.elist = [f"e{subscript_numbers[i]}" for i in range(1, 21)]
        self.zlist = [f"Z{subscript_numbers[i]}" for i in range(1, 21)]
        self.rlist = [f"r{subscript_numbers[i]}" for i in range(1, 21)]
        self.xlist = [f"x{subscript_numbers[i]}" for i in range(1, 21)]
        self.subscript_map = {
            '₀': '0',
            '₁': '1',
            '₂': '2',
            '₃': '3',
            '₄': '4',
            '₅': '5',
            '₆': '6',
            '₇': '7',
            '₈': '8',
            '₉': '9'
        }
      
        
    def extract_subscript_number(self,s):
           return int(''.join(self.subscript_map[c] for c in s if c in self.subscript_map))

        
        
  
