class State():
    counter = 0
    def __init__(self, accept):
        self.id = State.counter + 1
        self.links = {}
        self.accepting = accept
        State.counter += 1

    def __eq__(self, other):
        return self.id == other.id

    def __hash__(self):
        return hash(('id', self.id))

    def new_link(self, link, states):
        #If the link already exists, then we need to append the lists of states
        if link in self.links.keys():
            if type(states) == list:
                if type(self.links[link]) == list:
                    #If both the incoming states and the states already linked are lists of states, then combine the lists, then remove duplicates 
                    #(performing list(set(my_list)) on list, my_list, duplicates are removed)
                    self.links[link] = list(set(self.links[link] + states))
                else:
                    #If the incoming states are a list and the state that is already linked is not a list, then append the old states to the new states list
                    #Then set the object that this link points to as the list of new states + old state (with duplicates removed)
                    states.append(self.links[link])
                    self.links[link] = list(set(states))
            else:
                if type(self.links[link]) == list:
                    #If the incoming states is not a list and the pre-existing states is a list, then append the new state to the list of old states,
                    #with duplicates removed
                    self.links[link].append(states)
                    self.links[link] = list(set(self.links[link]))
                else:
                    #If neither the old nor the new states are a list of states, then, if the id's of the two states are not the same, create a new list that param link points to
                    if self.links[link].id != states.id:
                        self.links[link] = [self.links[link], states]
        else:
            #If the link does not already exist, then all we need to do is create the new link
            self.links[link] = states

    def change_accept(self):
        self.accepting = not self.accepting

class StateLinkPair():
    def __init__(self, link, state):
        self.link = link
        self.state = state
    def __eq__(self, other):
        return self.link == other.link and self.state == other.state

class Regex():
    def __init__(self, regex):
        self.regex   = regex
        self.start   = self.generate_states(self.regex)
        self.matches = {}
    def split(self, string):
        if not string in self.matches.keys():
            self.matches[string] = self.start_ends(self.start, string)
        sends = self.matches[string]
        print(sends)
        current_range  = 0
        current_string = ''
        splits_list    = []
        in_range_flag  = False
        loop = 0
        length = len(string)
        while loop < length:
            if not loop in range(sends[current_range][0], sends[current_range][1] + 1):
                
                current_string += string[loop]
            else:
                splits_list.append(current_string)
                current_string = ''
                current_range += 1
                in_range_flag = False
            loop += 1
        return splits_list
    def generate_states(self, regex):
        beginning_state = State(True)
        generate = self.machines(0)
        one, two, three = generate([beginning_state], [], regex)    
        if one == 'e' or two == 'e' or three == 'e':
            return None
        return beginning_state 

    def verify(self, start, string):
        '''
        verify recieves the starting state of the regex FSM and a string that will be checked against that regex
        verify returns a boolean True if the ENTIRE string matches the regex, 
            that is, if after every transition is made, we land at an accepting state, the whole string is accepted
        '''
        current_state = start
        loop = 0
        for transition in string:
            uni = False
            uni_state = None
            if 'Universal' in current_state.links.keys():
                uni = True
                uni_state = current_state.links['Universal']
            if transition in current_state.links.keys():
                next_state = current_state.links[transition]
            else:
                #print(False)
                if not uni:
                    return False
                else:
                    next_state = []
            if uni:
                if type(next_state) == list:
                    if type(uni_state) == list:
                        next_state += uni_state
                    else:
                        next_state.append(uni_state)
                else:
                    if type(uni_state) == list:
                        uni_state.append(next_state)
                        next_state = uni_state
                    else:
                        next_state = [next_state, uni_state]
            if type(next_state) == list:
                for state in next_state:
                    verified = verify(state, string[loop+1:])
                    if verified:
                        #print(True)
                        return True
                return False;
            else:
                current_state = next_state
            loop += 1
        #print(current_state.accepting)
        return current_state.accepting

    def start_ends(self, start, string):
        '''
        start_ends recieves the starting state of the regex FSM and a string that will be checked against that regex
        start_ends returns a set-list (every item is unique) of all subsections where the string matches the regex
            the format of this return is a list of tuples where:
                -    the first element of the tuple is the beginning, inclusive, index where the matching substring starts
                -    the second element of the tuple is the ending, exclusive, index where the matching substring ends
        '''
        ret = []
        length = len(string)
        if start.accepting:
            ret.append((0,1))
        for loop in range(length):
            current_state = start
            for inner_loop in range(loop,length):
                uni = False
                uni_state = None
                if 'Universal' in current_state.links.keys():
                    uni = True
                    uni_state = current_state.links['Universal']
                if string[inner_loop] in current_state.links.keys():
                    next_state = current_state.links[string[inner_loop]]
                else:
                    #print(False)
                    if not uni:
                        break
                    else:
                        next_state = []
                if uni:
                    if type(next_state) == list:
                        if type(uni_state) == list:
                            next_state += uni_state
                        else:
                            next_state.append(uni_state)
                    else:
                        if type(uni_state) == list:
                            uni_state.append(next_state)
                            next_state = uni_state
                        else:
                            next_state = [next_state, uni_state]
                if type(next_state) == list:
                    for state in next_state:
                        sends = start_ends(state, string[inner_loop+1:])
                        ret = ret + sends
                        ret = list(set(ret))
                    break
                else:
                    current_state = next_state
                    if next_state.accepting:
                        ret.append((loop, inner_loop))
                        ret = list(set(ret))
        ret.sort(reverse=True)
        skip = 0
        rem = []
        length = len(ret) 
        for loop, (beg, end) in enumerate(ret):
            if skip != 0:
                skip -= 1
                continue
            if loop != length - 1:
                for inner_loop, (inner_beg, inner_end) in enumerate(ret[loop+1:]):
                    if inner_loop != length - 1:
                        skip += 1
                        if beg >= inner_end:
                            skip -= 1
                            rem.append((beg, end))
                            break
            else:
                rem.append(ret[loop])
        rem = rem[::-1]
        return rem

    def machines(self, target):

        def find_in_array(target, array):
            '''
            Searches for a target variable in input array
            returns the index of the target if it is in the array, or None if target is not in the array
            '''
            length = len(array)
            for loop in range(length):
                if array[loop] == target:
                    return loop
            return None

        escape_characters    = ['.', '|', '?', '*', '+', '(', ')', '[', ']', '\\']
        special_characters   = ['s', 'S', 'd', 'D', 'w', 'W']
        border_characters    = ['|', '\\', '+', '*', '?', '(', '[', '{']
        '''
        s = whitespace (space, or tab)
        S = non-whitespace
        d = digit (0-9)
        D = non-digit (anything besides 0-9)
        w = word character (0-9, a-z, A-Z, _)
        W = non-word character (anything besides 0-9, a-z, A-Z, or _)
        '''
        def char_sequence_machine(accepting_states, complement_states, sequence, flip_accepting=True):
            if flip_accepting:
                for acc_state in accepting_states:
                    acc_state.accepting = False
            beginning_link_pairs = None
            #Seq is a sub-string of sequence
            #The way that this machine works is that it sub-strings, stored in seq, and executes them (builds the machine)
            #    whenever a 'border character' is found and then seq is reset
            seq = ''
            #List of sub-string sequences separated by '|' characters
            or_seqs = []
            #A flag set whenever a '(', '[', '|' is found, to search for the 'closing' character for this character
            find_next_border = False
            #Closing character: ')' corresponds to '(', ']' corresponds to '[', and '|' corresponds to '|',
            close = 'e'
            #Because for-loops in python are weird, I'm using a 'skip' integer to keep track of how many iterations to skip if I need to skip a loop
            skip = 0
            paren_count = 1
            length = len(sequence)
            if length <= 0:
                print('Error! Length of sequence {} is too short!'.format(sequence))
                return 'e', 'e', 'e'
            for loop in range(0, length):
                #Skip:
                if skip != 0:
                    skip -= 1
                    continue
                if not find_next_border:
                    if not sequence[loop] in border_characters:
                        if sequence[loop] != '.':
                            seq += sequence[loop]
                        else:
                            if seq != '':
                                accepting_states, complement_states, temp_links = char_sequence_machine(accepting_states, complement_states, seq)
                                if accepting_states == 'e' or complement_states == 'e' or temp_links == 'e':
                                    return 'e', 'e', 'e'
                                if beginning_link_pairs is None:
                                    beginning_link_pairs = temp_links
                            
                            if loop != length - 1:
                                skip = 0
                                if sequence[loop + 1] == '*' or sequence[loop + 1] == '+' or sequence[loop + 1] == '?':
                                    add_to_link_pairs = False
                                    if beginning_link_pairs is None:
                                        beginning_link_pairs = []
                                        add_to_link_pairs = True
                                    next_state = State(True)
                                    for acc_state in accepting_states:
                                        acc_state.accepting = (sequence[loop + 1] == '*' or sequence[loop + 1] == '?')
                                        acc_state.new_link('Universal', next_state)
                                        if add_to_link_pairs:
                                            beginning_link_pairs.append(StateLinkPair('Universal', acc_state))
                                    if sequence[loop + 1] == '*' or sequence[loop + 1] == '?':
                                        accepting_states.append(next_state)
                                    else:
                                        accepting_states = [next_state]
                                    if sequence[loop + 1] == '*' or sequence[loop + 1] == '+':
                                        next_state.new_link('Universal', next_state)
                                    skip += 1
                                elif sequence[loop + 1] == '{':
                                    #Curly machine doing
                                    if loop + 2 == length - 1:
                                        if sequence[loop + 2] == '}':
                                            add_to_link_pairs = False
                                            if beginning_link_pairs is None:
                                                beginning_link_pairs = []
                                                add_to_link_pairs = True
                                            next_state = State(True)
                                            for acc_state in accepting_states:
                                                acc_state.accepting = False
                                                acc_state.new_link('Universal', next_state)
                                                if add_to_link_pairs:
                                                    beginning_link_pairs.append(StateLinkPair('Universal', acc_state))
                                            accepting_states = [next_state]
                                            skip = 2
                                            seq = '{}'
                                            continue
                                        else:
                                            print("Error! Hanging bracket!")
                                            return 'e', 'e', 'e'
                                    skip += 1
                                    end_curl_found = False
                                    curly_phrase = ''
                                    #Searching for whole phrase enclosed by {}
                                    #If end_curl_found is not set to True, the regex is invalid
                                    for inner_loop in range(loop+2,length):
                                        skip += 1
                                        if sequence[inner_loop] == '}':
                                            end_curl_found = True
                                            break
                                        curly_phrase += sequence[inner_loop]
                                    if not end_curl_found:
                                        print("Error! No ending bracket in {}".format(sequence))
                                        return 'e', 'e', 'e'
                                    else:
                                        #The code for a {} is too complicated to recreate here, even for a single character phrase, so we just call curly_machine method to do it for us
                                        accepting_states, complement_states, temp_links = curly_machine(accepting_states, complement_states, '.', curly_phrase)
                                        if accepting_states == 'e' or complement_states == 'e' or temp_links == 'e':
                                            return 'e', 'e', 'e'
                                        #We only need to keep track of the beginning link pairs for the very beginning of the sequence machine, so if beginning_link_pairs is still None
                                        #    we reset beginning_link_pairs
                                        if beginning_link_pairs is None:
                                            beginning_link_pairs = temp_links
                                else:
                                    add_to_link_pairs = False
                                    if beginning_link_pairs is None:
                                        beginning_link_pairs = []
                                        add_to_link_pairs = True
                                    next_state = State(True)
                                    for acc_state in accepting_states:
                                        acc_state.accepting = False
                                        acc_state.new_link('Universal', next_state)
                                        if add_to_link_pairs:
                                            beginning_link_pairs.append(StateLinkPair('Universal', acc_state))
                                    accepting_states = [next_state]
                            else:
                                add_to_link_pairs = False
                                if beginning_link_pairs is None:
                                    beginning_link_pairs = []
                                    add_to_link_pairs = True
                                next_state = State(True)
                                for acc_state in accepting_states:
                                    acc_state.accepting = False
                                    acc_state.new_link('Universal', next_state)
                                    if add_to_link_pairs:
                                        beginning_link_pairs.append(StateLinkPair('Universal', acc_state))
                                accepting_states = [next_state]


                            seq = ''
                    else:
                        if (sequence[loop] == '|' or sequence[loop] == '*' or sequence[loop] == '+') and seq == '':
                            print("Error! Hanging '{}' character!".format(sequence[loop]))
                            return 'e', 'e', 'e'
                        else:
                            if sequence[loop] == '|':
                                find_next_border = True
                                or_seqs.append(seq)
                                close = '|'
                                seq = ''
                            elif sequence[loop] == '\\':
                                if loop != length - 1:
                                    res_esc  = find_in_array(sequence[loop + 1], escape_characters)
                                    res_spec = find_in_array(sequence[loop + 1], special_characters)
                                    if not res_esc is None:
                                        esc = sequence[loop + 1]
                                        seq += esc
                                        skip = 1
                                    elif not res_spec is None:
                                        spec = sequence[loop + 1]
                                        if seq != '':
                                            accepting_states, complement_states, temp_links = char_sequence_machine(accepting_states, complement_states, seq)
                                            if accepting_states == 'e' or complement_states == 'e' or temp_links == 'e':
                                                return 'e', 'e', 'e'
                                            if beginning_link_pairs is None:
                                                beginning_link_pairs = temp_links
                                        spec_char_dict = {'s':'[ \t\r\n\f]', 'S':'[^ \t\r\n\f]', 'd':'[0-9]', 'D':'[^0-9]', 'w':'[A-Za-z0-9_]', 'W':'[^A-Za-z0-9_]'}
                                        skip = 1
                                        if loop != length - 2: 
                                            if sequence[loop + 2] == '*' or sequence[loop + 2] == '+' or sequence[loop + 2] == '?':
                                                
                                                function_dict = {'*': star_machine, '+': plus_machine, '?': question_machine}
                                                function = function_dict[sequence[loop + 2]]                                        
                                                accepting_states, complement_states, temp_links = function(accepting_states, complement_states, (spec_char_dict[spec]))
                                                if accepting_states == 'e' or complement_states == 'e' or temp_links == 'e':
                                                    return 'e', 'e', 'e'
                                                if beginning_link_pairs is None:
                                                    beginning_link_pairs = temp_links
                                                skip += 1
                                            elif sequence[loop + 2] == '{':
                                                #Curly machine doing
                                                if loop + 3 == length - 1:
                                                    if sequence[loop + 3] == '}':
                                                        accepting_states, complement_states, temp_links = char_sequence_machine(accepting_states, complement_states, (spec_char_dict[spec]))
                                                        if accepting_states == 'e' or complement_states == 'e' or temp_links == 'e':
                                                            return 'e', 'e', 'e'
                                                        if beginning_link_pairs is None:
                                                            beginning_link_pairs = temp_links
                                                        skip = 3
                                                        seq = '{}'
                                                        continue
                                                    else:
                                                        print("Error! Hanging bracket!")
                                                        return 'e', 'e', 'e'
                                                skip += 1
                                                end_curl_found = False
                                                curly_phrase = ''
                                                #Searching for whole phrase enclosed by {}
                                                #If end_curl_found is not set to True, the regex is invalid
                                                for inner_loop in range(loop+2,length):
                                                    skip += 1
                                                    if sequence[inner_loop] == '}':
                                                        end_curl_found = True
                                                        break
                                                    curly_phrase += sequence[inner_loop]
                                                if not end_curl_found:
                                                    print("Error! No ending bracket in {}".format(sequence))
                                                    return 'e', 'e', 'e'
                                                else:
                                                    #The code for a {} is too complicated to recreate here, even for a single character phrase, so we just call curly_machine method to do it for us
                                                    accepting_states, complement_states, temp_links = curly_machine(accepting_states, complement_states, (spec_char_dict[spec]), curly_phrase)
                                                    if accepting_states == 'e' or complement_states == 'e' or temp_links == 'e':
                                                        return 'e', 'e', 'e'
                                                    #We only need to keep track of the beginning link pairs for the very beginning of the sequence machine, so if beginning_link_pairs is still None
                                                    #    we reset beginning_link_pairs
                                                    if beginning_link_pairs is None:
                                                        beginning_link_pairs = temp_links
                                            else:
                                                accepting_states, complement_states, temp_links = char_set_machine(accepting_states, complement_states, (spec_char_dict[spec])[1:-1:1])
                                                if accepting_states == 'e' or complement_states == 'e' or temp_links == 'e':
                                                    return 'e', 'e', 'e'
                                                if beginning_link_pairs is None:
                                                    beginning_link_pairs = temp_links
                                        else:
                                            accepting_states, complement_states, temp_links = char_set_machine(accepting_states, complement_states, (spec_char_dict[spec])[1:-1:1])
                                            if accepting_states == 'e' or complement_states == 'e' or temp_links == 'e':
                                                return 'e', 'e', 'e'
                                            if beginning_link_pairs is None:
                                                beginning_link_pairs = temp_links
                                        seq = ''
                                        
                                    else:
                                        print("Error! Hanging escape character, '\\', in sequence '{}'!".format(sequence))
                                        return 'e', 'e', 'e'
                                else:
                                    print("Error! Hanging escape character, '\\', in sequence '{}'!".format(sequence))
                                    return 'e', 'e', 'e'
                            elif sequence[loop] == '[' or sequence[loop] == '(':
                                #If char is '[' but the next char is ']', or char is '(' but the next char is ')'
                                #    then they are just characters in a sequence, 
                                #    add them to the sequence and continue with next loop
                                if loop != length - 1:
                                    if sequence[loop] == '[':
                                        if sequence[loop + 1] == ']':
                                            seq += '[]'
                                            skip = 1
                                            continue
                                        #If char is '[' and next char is not ']', then closing character for the phrase is ']'
                                        else:
                                            close = ']'
                                    if sequence[loop] == '(':
                                        if sequence[loop + 1] == ')':
                                            seq += '()'
                                            skip = 1
                                            continue
                                        #If char is '(' and next char is not ')', then closing character for the phrase is ')'
                                        else:
                                            close = ')'
                                else:
                                    print("Error! Hanging '{}' in sequence '{}'!".format(sequence[loop], sequence))
                                    return 'e', 'e', 'e'
                                find_next_border = True
                                add_to_link_pairs = False
                                if beginning_link_pairs is None:
                                    beginning_link_pairs = []
                                    add_to_link_pairs = True
                                seq_len = len(seq)
                                if seq_len >= 1:
                                    for inner_loop in range(seq_len):
                                        #Creates the next states in the machine
                                        next_state = State(False)
                                        #For all previous accepting states, create a link
                                        #    to the new state using the current character in seq
                                        #    as the transition, and set all the acceptance of
                                        #    all states to false
                                        for acc_state in accepting_states:
                                            acc_state.accepting = False
                                            acc_state.new_link(seq[inner_loop], next_state)
                                            if add_to_link_pairs:
                                                beginning_link_pairs.append(StateLinkPair(seq[inner_loop], acc_state))
                                        #Because the machine is sequential, the list of accepting
                                        #    states for the next machine (or iteration of the loop)
                                        #    is simply a list containing the newly created states
                                        accepting_states  = [next_state]
                                        add_to_link_pairs = False
                                seq = ''
                                find_next_border = True
                            elif sequence[loop] == '*' or sequence[loop] == '+' or sequence[loop] == '?' or sequence[loop] == '{':
                                #If char is '{' but the next char is '}', then they are just characters in a sequence, 
                                #    add them to the sequence and continue with next loop
                                if sequence[loop] == '{' and loop != length - 1 and sequence[loop + 1] == '}':
                                    seq += '{'
                                    continue
                                #Storing the repeating character for later
                                rep = seq[-1]
                                #This is the length of the previous sequence BEFORE
                                #    the repeating character 
                                #    (and, thus, before the current '*' or '+')
                                seq_len = len(seq) - 1
                                #Adding states to the machine for all characters in seq, 
                                #    excluding the repeating character 
                                add_to_link_pairs = False
                                if beginning_link_pairs is None:
                                    beginning_link_pairs = []
                                    add_to_link_pairs = True
                                for inner_loop in range(seq_len):
                                    #Creates the next states in the machine
                                    next_state = State(False)
                                    #For all previous accepting states, create a link
                                    #    to the new state using the current character in seq
                                    #    as the transition, and set all the acceptance of
                                    #    all states to false
                                    for acc_state in accepting_states:
                                        acc_state.accepting = False
                                        acc_state.new_link(seq[inner_loop], next_state)
                                        if add_to_link_pairs:
                                            beginning_link_pairs.append(StateLinkPair(seq[inner_loop], acc_state))
                                    #Because the machine is sequential, the list of accepting
                                    #    states for the next machine (or iteration of the loop)
                                    #    is simply a list containing the newly created states
                                    accepting_states  = [next_state]
                                    add_to_link_pairs = False
                                if sequence[loop] == '*' or sequence[loop] == '+' or sequence[loop] == '?':
                                    next_state = State(True)
                                    #Now that seq (up to len - 1) is dealt with, we add the
                                    #    repeating character to the machine, and then set a
                                    #    transition from itself to itself
                                    for acc_state in accepting_states:
                                         #If current character is a star, then the prev 
                                         #    sequence can be repeated 0 or more times, so 
                                         #    the previous accepting states remain as 
                                         #    accepting states
                                         #Thus, the accepting status of the previous accepting
                                         #    states is (sequence[loop] == '*'), a boolean
                                        acc_state.accepting = (sequence[loop] == '*' or sequence[loop] == '?')
                                        acc_state.new_link(rep, next_state)
                                    if sequence[loop] != '?':
                                        next_state.new_link(rep, next_state)
                                    #If the repeating symbol is a *, then the old accepting states
                                    #    must remain in the accepting states list because the sequence
                                    #    can repeat 0 or more times
                                    if sequence[loop] == '*' or sequence[loop] == '?':
                                        accepting_states.append(next_state)
                                    else:
                                        accepting_states = [next_state]
                                else:
                                    if loop != length - 1:
                                        skip = 0
                                        end_curl_found = False
                                        curly_phrase = ''
                                        #Searching for whole phrase enclosed by {}
                                        #If end_curl_found is not set to True, the regex is invalid
                                        for inner_loop in range(loop+1,length):
                                            skip += 1
                                            if sequence[inner_loop] == '}':
                                                end_curl_found = True
                                                break
                                            curly_phrase += sequence[inner_loop]
                                        if not end_curl_found:
                                            print("Error! No ending bracket in {}".format(sequence))
                                            return 'e', 'e', 'e'
                                        else:
                                            #The code for a {} is too complicated to recreate here, even for a single character phrase, so we just call curly_machine method to do it for us
                                            accepting_states, complement_states, temp_links = curly_machine(accepting_states, complement_states, rep, curly_phrase)
                                            if accepting_states == 'e' or complement_states == 'e' or temp_links == 'e':
                                                return 'e', 'e', 'e'
                                            #We only need to keep track of the beginning link pairs for the very beginning of the sequence machine, so if beginning_link_pairs is still None
                                            #    we reset beginning_link_pairs
                                            if beginning_link_pairs is None:
                                                beginning_link_pairs = temp_links
                                    else:
                                        print("Error! No ending bracket in {}".format(sequence))
                                        return 'e', 'e', 'e'
                                #Reset seq
                                seq = ''
                else:
                    if sequence[loop] != close:
                        seq += sequence[loop]
                        if sequence[loop] == '(':
                            paren_count += 1
                    else:
                        if close == '|':
                            or_seqs.append(seq)
                            seq = ''    
                        if close == ')':
                            paren_count -= 1
                            if paren_count != 0:
                                seq += ')'
                        if (close == ')' and paren_count == 0) or close == ']':
                            if loop != length - 1:
                                if sequence[loop + 1] == '*' or sequence[loop + 1] == '+' or sequence[loop + 1] == '?':
                                
                                    function_dict = {'*': star_machine, '+': plus_machine, '?': question_machine}
                                    function = function_dict[sequence[loop + 1]]

                                    if close == ')':
                                        accepting_states, complement_states, temp_links = function(accepting_states, complement_states, seq)
                                    else:
                                        accepting_states, complement_states, temp_links = function(accepting_states, complement_states, '[' + seq + ']')
                                    if accepting_states == 'e' or complement_states == 'e' or temp_links == 'e':
                                        return 'e', 'e', 'e'
                                    if beginning_link_pairs is None:
                                        beginning_link_pairs = temp_links
                                    skip = 1
                                    find_next_border = False
                                    close = 'e'
                                    seq = ''
                                elif loop != length - 1 and sequence[loop + 1] == '{':
                                    #Curly machine doing
                                    if loop + 1 == length - 1:
                                        if sequence[loop + 2] == '}':
                                            if close == ')':
                                                accepting_states, complement_states, temp_links = char_sequence_machine(accepting_states, complement_states, seq)
                                            else:
                                                accepting_states, complement_states, temp_links = char_sequence_machine(accepting_states, complement_states, '[' + seq + ']')
                                            if accepting_states == 'e' or complement_states == 'e' or temp_links == 'e':
                                                return 'e', 'e', 'e'
                                            if beginning_link_pairs is None:
                                                beginning_link_pairs = temp_links
                                            close = 'e'
                                            find_next_border = False
                                            skip = 2
                                            seq = '{}'
                                        else:
                                            print("Error! Hanging bracket!")
                                            return 'e', 'e', 'e'
                                    skip = 1
                                    end_curl_found = False
                                    curly_phrase = ''
                                    #Searching for whole phrase enclosed by {}
                                    #If end_curl_found is not set to True, the regex is invalid
                                    for inner_loop in range(loop+2,length):
                                        skip += 1
                                        if sequence[inner_loop] == '}':
                                            end_curl_found = True
                                            break
                                        curly_phrase += sequence[inner_loop]
                                    if not end_curl_found:
                                        print("Error! No ending bracket in {}".format(sequence))
                                        return 'e', 'e', 'e'
                                    else:
                                        #The code for a {} is too complicated to recreate here, even for a single character phrase, so we just call curly_machine method to do it for us
                                        if close == ')':
                                            accepting_states, complement_states, temp_links = curly_machine(accepting_states, complement_states, seq, curly_phrase)
                                        else:
                                            accepting_states, complement_states, temp_links = curly_machine(accepting_states, complement_states, '[' + seq + ']', curly_phrase)
                                        if accepting_states == 'e' or complement_states == 'e' or temp_links == 'e':
                                            return 'e', 'e', 'e'
                                        #We only need to keep track of the beginning link pairs for the very beginning of the sequence machine, so if beginning_link_pairs is still None
                                        #    we reset beginning_link_pairs
                                        if beginning_link_pairs is None:
                                            beginning_link_pairs = temp_links
                                    find_next_border = False
                                    close = 'e'
                                    seq = ''
                                else:
                                    if close == ')':
                                        accepting_states, complement_states, temp_links = char_sequence_machine(accepting_states, complement_states, seq)
                                    else:
                                        accepting_states, complement_states, temp_links = char_set_machine(accepting_states, complement_states, seq)
                                    if accepting_states == 'e' or complement_states == 'e' or temp_links == 'e':
                                        return 'e', 'e', 'e'
                                    if beginning_link_pairs is None:
                                        beginning_link_pairs = temp_links
                                    find_next_border = False
                                    close = 'e'
                                    seq = ''
                            else:
                                if close == ')':
                                    accepting_states, complement_states, temp_links = char_sequence_machine(accepting_states, complement_states, seq)
                                else:
                                    accepting_states, complement_states, temp_links = char_set_machine(accepting_states, complement_states, seq)
                                if accepting_states == 'e' or complement_states == 'e' or temp_links == 'e':
                                    return 'e', 'e', 'e'
                                if beginning_link_pairs is None:
                                    beginning_link_pairs = temp_links
                                find_next_border = False
                                close = 'e'
                                seq = ''
            if find_next_border:
                if close == '|':
                    or_seqs.append(seq)
                    new_accepts = []
                    new_comps   = []
                    for phrase in or_seqs:
                        temp_accepts, temp_comps, temp_links = char_sequence_machine(accepting_states, complement_states, phrase)
                        if temp_accepts == 'e' or temp_comps == 'e' or temp_links == 'e':
                            return 'e', 'e', 'e'
                        new_accepts.append(temp_accepts)
                        new_comps.append(temp_comps)
                        if beginning_link_pairs is None:
                            beginning_link_pairs = temp_links
                    return new_accepts, new_comps, beginning_link_pairs     
                #If close == ')' or close == ']', and we've reached the end of sequence, then throw an error
                else:
                    print("Error! Missing closing '{}' character in sequence '{}'!".format(close, sequence))
                    return 'e', 'e', 'e'
            elif seq != '':
                seq_len = len(seq)
                add_to_link_pairs = False
                if beginning_link_pairs is None:
                    beginning_link_pairs = []
                    add_to_link_pairs = True
                for inner_loop in range(seq_len):
                    #Creates the next states in the machine
                    next_state = State(False)
                    #For all previous accepting states, create a link
                    #    to the new state using the current character in seq
                    #    as the transition, and set all the acceptance of
                    #    all states to false
                    for acc_state in accepting_states:
                        acc_state.accepting = False
                        acc_state.new_link(seq[inner_loop], next_state)
                        if add_to_link_pairs:
                            beginning_link_pairs.append(StateLinkPair(seq[inner_loop], acc_state))
                    #Because the machine is sequential, the list of accepting
                    #    states for the next machine (or iteration of the loop)
                    #    is simply a list containing the newly created states
                    accepting_states  = [next_state]
                    add_to_link_pairs = False
                for acc_state in accepting_states:
                    acc_state.accepting = True
            return accepting_states, complement_states, beginning_link_pairs

        def char_set_machine(accepting_states, complement_states, sequence, target=None, flip_accepting=True):
            '''
            Builds a state that gets pointed to by all previous accepting states according to a character set built from @param: sequence
            accepting_states  = the accepting states of the previous machine
            complement_states = the non-accepting states of the previous machine
            sequence          = the text of the character set, excluding opening and closing '[]' square brackets
            returns the list of accepting states, complementary states, and StateLinkPairs that lead to the beginning states of the new machine
            '''
            if flip_accepting:
                for acc_state in accepting_states:
                    acc_state.accepting = False
            if target is None:
                accept = State(True)
            else:
                accept = target
            skip = 0
            beg_index  = 0
            inv_list   = []
            do_not_add = []
            prev_back  = False
            inverse    = False
            length     = len(sequence)
            if length <= 0:
                print('Error! Length of sequence {} is too short!'.format(sequence))
                return 'e', 'e', 'e'
            beginning_link_pairs = []
            #Edge cases testing:
            if length > 1:
                if sequence[0] == '^' and sequence[1] != '-':
                    beg_index += 1
                    inverse = True
                elif sequence[0] == '-':
                    beg_index += 1
                    for acc_state in accepting_states:
                        acc_state.new_link('-', accept)
            for loop in range(beg_index, length):
                if skip > 0:
                    skip -= 1
                    continue
                if sequence[loop] in escape_characters and not prev_back:
                    print("Error! No escape character on escapable character '{}'!".format(sequence[loop]))
                    return 'e', 'e', 'e'
                if sequence[loop] != '\\':
                    if loop < length - 2 and sequence[loop + 1] == '-':
                        add = 2
                        skip = 2
                        if sequence[loop + 2] == '\\':
                            if sequence[loop + 3] in escape_characters or sequence[loop + 3] == '\\':
                                add += 1
                                skip += 1
                            elif sequence[loop + 3] in special_characters:
                                print('Error! Special characters like \\{} cannot be included in ranges such as {}'.format(sequence[loop + 3], sequence))
                                return 'e', 'e', 'e'
                            else:
                                print('Error! {} in [{}] is not an escape character but it is preceeded by \\!'.format(sequence[loop + 3], sequence))
                                return 'e', 'e', 'e'
                        elif sequence[loop + 2] in escape_characters:
                            print('Error! [{}] has invalid ending character!'.format(sequence))
                            return 'e', 'e', 'e'
                        useless, useless, temp_links, temp_no_add = in_range(accepting_states, complement_states, (sequence[loop] + '-' + sequence[loop + add]), accept, inverse)
                        if useless == 'e' or useless == 'e' or beginning_link_pairs == 'e':
                            return 'e', 'e', 'e'
                        beginning_link_pairs = beginning_link_pairs + temp_links
                        do_not_add = do_not_add + temp_no_add
                    else:
                        #Normal cases of adding links.  These cover [a],[ab],[abc], etc...
                        #    All cases where there are no '\' before the character and no '-' after it
                        for acc_state in accepting_states:
                            if not inverse:
                                beginning_link_pairs.append(StateLinkPair(sequence[loop], acc_state))
                                acc_state.new_link(sequence[loop], accept)
                            else:
                                inv_list.append(sequence[loop])
                else:
                    focus = sequence[loop + 1]
                    res = find_in_array(focus, special_characters)
                    if focus in escape_characters:
                        prev_back = True
                    elif not res is None:
                        if res <= 5:
                            spec_char_dict = {'s':'^ \t\r\n\f', 'S':'^ \t\r\n\f', 'd':'^0-9', 'D':'^0-9', 'w':'^A-Za-z0-9_', 'W':'^A-Za-z0-9_'}
                            start = 1
                            alt = 0
                            if res % 2 != 0:
                                start = 0
                                alt = 1
                            if inverse:
                                start = alt
                            useless, useless, temp = char_set_machine(accepting_states, complement_states, (spec_char_dict[focus])[start:], accept)
                            if useless == 'e' or useless == 'e' or beginning_link_pairs == 'e':
                                return 'e', 'e', 'e'
                            beginning_link_pairs = beginning_link_pairs + temp
                        skip = 1

                    else:
                        print("Error! Non-escapable character {} is preceded by the escape character '\\'".format(sequence[loop + 1]))
                        return 'e', 'e', 'e'
            if inverse:
                for loop in range(128):
                    char = chr(loop)
                    if not (char in inv_list or char in do_not_add):
                        for acc_state in accepting_states:
                            beginning_link_pairs.append(StateLinkPair(char, acc_state))
                            acc_state.new_link(char, accept)
            return [accept], complement_states, beginning_link_pairs

        def in_range(accepting_states, complement_states, sequence, target=None, inverse=False):
            '''
            Builds a state that gets pointed to by all previously accepting states by all characters within the range of @param: sequence
            accepting_states  = the accepting states of the previous machine
            complement_states = the non-accepting states of the previous machine
            sequence          = the range sequence of characters that will be included for the links (e.g. '0-9', 'a-z', '!-~', etc.)
            returns the list of accepting states, complementary states, and StateLinkPairs that lead to the beginning states of the new machine
            '''
            #Sometimes, this method will be called with an additional argument that is the pointer to the state that the links in the range point to
            #    When this happens, ret is set to the 'target' state instead of the new state denoted by State(True)
            if target is None:
                ret = State(True)
            else:
                ret = target

            length = len(sequence)
            if length <= 0:
                print('Error! Length of sequence {} is too short!'.format(sequence))
                return 'e', 'e', 'e'
            #Retrieving the integer values of the beginning and ending characters in the sequence
            begin = ord(sequence[0])
            end  = ord(sequence[-1])
            do_not_add = []
            #Testing to make sure that the beginning and ending of the range logically makes sense
            if begin > end:
                print('Error! [{}] out of range!'.format(sequence))
                return 'e', 'e', 'e'
            #Initializing the list of StateLinkPairs that will be returned by this function
            beginning_link_pairs = []
            #If additional argument, inverse, is false then for-loop adds all the 
            #    characters in the range first to the the list of LinkStatePairs, 
            #    beginning_link_pair, then to the links of all the accepting states 
            #    in accepting_states
            if not inverse:
                for transition in range(begin, end+1):
                    for acc_state in accepting_states:
                        acc_state.new_link(chr(transition), ret)
                        beginning_link_pairs.append(StateLinkPair(chr(transition), acc_state))
            #If additional argument, inverse, is true, then we add everything NOT in that range of characters
            else:
                #First, by adding all the character lower than the beginning character
                for transition in range(0, 128):
                    if transition >= begin and transition <= end:
                        do_not_add.append(chr(transition))
            return [ret], accepting_states, beginning_link_pairs, do_not_add

        def star_machine(accepting_states, complement_states, sequence):
            '''
            Builds a sequence of states that behave like a '*' machine
            accepting_states  = the accepting states of the previous machine
            complement_states = the non-accepting states of the previous machine
            sequence          = the string of characters modified by the '*'
                                    for example: sequence = 'a' where regex = 'a*'
                                                 sequence = 'aab' where regex = '(aab)*'
            returns the list of accepting states, complementary states, and StateLinkPairs that lead to the beginning states of the new machine
            '''
            length = len(sequence)
            if length <= 0:
                print('Error! Length of sequence {} is too short!'.format(sequence))
                return 'e', 'e', 'e'
            #Need to keep track of old accepting states for the next machine, because the '*' means that these will remain as accepting states for the next machine
            new_accepts = accepting_states.copy()
            #Calls char_sequence_machine on sequence to build a machine for string sequence being modified by '*'
            #The flip_accepting parameter is set to false, so that the accepting states remain accepting
            accepting_states, complement_states, beginning_link_pairs = char_sequence_machine(accepting_states, complement_states, sequence, False)
            if accepting_states == 'e' or complement_states == 'e' or beginning_link_pairs == 'e':
                return 'e', 'e', 'e'
            for acc_state in new_accepts:
                acc_state.accepting = True
            #Nested for-loop links all the accepting states of the 'sequence' machine (built above) to the beginning states of the 'sequence' machine
            for pair in beginning_link_pairs:
                state = pair.state
                link  = pair.link
                destination  = state.links[link]
                for accept in accepting_states:
                    accept.new_link(link, destination)
            #Because accepting_states is being reset on the line above (to the accepting states of the 'sequence' machine) we need to add the new accepting states to the old accepting states 
            new_accepts = new_accepts + accepting_states
            return new_accepts, complement_states, beginning_link_pairs

        def plus_machine(accepting_states, complement_states, sequence):
            '''
            Builds a sequence of states that behave like a '+' machine
            accepting_states  = the accepting states of the previous machine
            complement_states = the non-accepting states of the previous machine
            sequence          = the string of characters modified by the '+'
                                    for example: sequence = 'a' where regex = 'a+'
                                                 sequence = 'aab' where regex = '(aab)+'
            returns the list of accepting states, complementary states, and StateLinkPairs that lead to the beginning states of the new machine
            '''
            length = len(sequence)
            if length <= 0:
                print('Error! Length of sequence {} is too short!'.format(sequence))
                return 'e', 'e', 'e'
            #Calls char_sequence_machine on sequence to build a machine for string sequence being modified by '+'
            #The flip_accepting parameter is set to True so that the accepting states will become non-accepting states (due to the '+' modifier)
            accepting_states, complement_states, beginning_link_pairs = char_sequence_machine(accepting_states, complement_states, sequence, True)
            if accepting_states == 'e' or complement_states == 'e' or beginning_link_pairs == 'e':
                return 'e', 'e', 'e'
            #Nested for-loop links all the accepting states of the 'sequence' machine (built above) to the beginning states of the 'sequence' machine
            for pair in beginning_link_pairs:
                state = pair.state
                link  = pair.link
                destination  = state.links[link]
                for accept in accepting_states:
                    accept.new_link(link, destination)
            #Returns the accepting states, the complement states, and the links pairs of the char_sequence_machine of above
            return accepting_states, complement_states, beginning_link_pairs

        def question_machine(accepting_states, complement_states, sequence):
            '''
            Builds a sequence of states that behave like a '?' machine
            accepting_states  = the accepting states of the previous machine
            complement_states = the non-accepting states of the previous machine
            sequence          = the string of characters modified by the '?'
                                    for example: sequence = 'a' where regex = 'a?'
                                                 sequence = 'aab' where regex =  '(aab)?'
            returns the list of accepting states, complementary states, and StateLinkPairs that lead to the beginning states of the new machine
            '''
            length = len(sequence)
            if length <= 0:
                print('Error! Length of sequence {} is too short!'.format(sequence))
                return 'e', 'e', 'e'
            #Need to keep track of old accepting states for the next machine, because the '?' means that these will remain as accepting states for the next machine
            new_accepts = accepting_states.copy()
            #Calls char_sequence_machine on sequence to build a machine for string sequence being modified by '?'
            #The flip_accepting parameter is set to false, so that the accepting states remain accepting
            accepting_states, complement_states, beginning_link_pairs = char_sequence_machine(accepting_states, complement_states, sequence, False)
            if accepting_states == 'e' or complement_states == 'e' or beginning_link_pairs == 'e':
                return 'e', 'e', 'e'
            #Because accepting_states is being reset on the line above (to the accepting states of the 'sequence' machine) we need to add the new accepting states to the old accepting states 
            new_accepts = new_accepts + accepting_states
            return new_accepts, complement_states, beginning_link_pairs

        def curly_machine(accepting_states, complement_states, sequence, curls):
            '''
            Builds a sequence of states that behave like a {} machine
            accepting_states  = the list of accepting states of the previous machine
            complement_states = the list of non-accepting states of the previous machine
            sequence          = the string sequence that is being repeated by the curly_machine
            curls             = the string sequence of characters inside the {} brackets
            returns the list of accepting states, complementary states, and StateLinkPairs that lead to the beginning states of the new machine
            '''
            length = len(sequence)
            if length <= 0:
                print('Error! Length of sequence {} is too short!'.format(sequence))
                return 'e', 'e', 'e'
            curl_splits = curls.strip().split(',')
            #default values of min and max repeats are 'd'
            #For sequences of format {#1}: min = #1, max = 'm' ('max is min')
            #For sequences of format {#1,}: min = #1, max = 'n' ('no max')
            #For sequences of format {#1,#2}: min = #1, max = #2
            min_reps = 'd'
            max_reps = 'd'
            beginning_link_pairs = []
            #str -> int conversions
            if len(curl_splits) == 1:
                try:
                    min_reps = int(curl_splits[0])
                    max_reps = 'm'
                except:
                    print('Error! Non-integer value in {}!'.format(sequence))
                    return 'e', 'e', 'e'
            elif len(curl_splits) == 2:
                if curl_splits[1] == '':
                    try:
                        min_reps = int(curl_splits[0])
                        max_reps = 'n'
                    except:
                        print('Error! Non-integer value in {}!'.format(sequence))
                        return 'e', 'e', 'e'
                else:
                    try:
                        min_reps = int(curl_splits[0])
                        max_reps = int(curl_splits[1])
                    except:
                        print('Error! Non-integer value in {}!'.format(sequence))
                        return 'e', 'e', 'e'
            #If min_reps == 0 and max reps is 'e', then the format of the sequence is:
            #    sequence = {0} 
            #    This sequence does not make any logical sense, so the method returns a half-error 'n', 'n', 'n'
            #    When this half-error is returned to the caller (char_sequence_machine()), it knows to not make any changes to the Finite-State machine
            '''if min_reps == 0 and max_reps == 'e':
                return accepting_states, complement_states, None'''
            #If max is smaller than min, obviously the sequence is out of order, return an error
            if max_reps != 'e'and max_reps != 'n' and max_reps != 'm':
                if  max_reps < min_reps:
                    print('Error! Sequence {} out of range!'.format(sequence))
                    return 'e', 'e', 'e'
                if min_reps < 0 or max_reps < 0:
                    print('Error! Sequence {} has an illogical range!'.format(sequence))
                    return 'e', 'e', 'e'
                if max_reps == min_reps:
                    max_reps = 'm'
            
            #Variables initialized
            new_accepts          = []
            new_comps            = []
            new_link             = []
            temp_accepts         = accepting_states.copy()
            temp_complements     = complement_states.copy()
            temp_beginning_links = beginning_link_pairs.copy()

            #If the minimum repeats is higher than zero, build the machine min_reps # of times
            if min_reps > 0:
                #Building machine
                for loop in range(min_reps):
                    for acc_state in accepting_states:
                        temp_accepts, temp_complements, temp_beginning_links = char_sequence_machine(temp_accepts, temp_complements, sequence)
                        if temp_accepts == 'e' or temp_complements == 'e' or temp_beginning_links == 'e':
                            return 'e', 'e', 'e'
                        #Only keep track of the link_pairs to the first instance of the machine
                        if loop == 0:
                            new_link = temp_beginning_links + new_link
                for acc_state in temp_accepts:
                    acc_state.accepting = True
            else:
                #If min repeats == 0, build the sequence machine and DO NOT flips the accepting states from the last machine
                temp_accepts, temp_complements, temp_beginning_links = char_sequence_machine(accepting_states, complement_states, sequence, False)
                if temp_accepts == 'e' or temp_complements == 'e' or temp_beginning_links == 'e':
                    return 'e', 'e', 'e'
                #New accepting states is composed of the old accepting states, and the accepting states from the new sequence machine just built 
                new_accepts = temp_accepts + new_accepts
                new_comps   = temp_complements + new_comps
                #Keep the link-pairs to the beginning of the machine
                new_link   = temp_beginning_links + new_link
            #If an end range exists, then create instances of the sequence machine totalling max_reps - min_reps
            #In each new machine, the accepting states of the last ones are not flipped and are stored in new_accepts
            #Accepting states are not flipped because {1,5} implies the phrase can be accepted 1, 2, 3, 4, or 5 times
            if max_reps != 'n' and max_reps != 'm':
                #Machines being built
                for loop in range(max_reps - min_reps):
                    for acc_state in accepting_states:
                        temp_accepts, temp_complements, temp_beginning_links = char_sequence_machine(temp_accepts, temp_complements, sequence, False)
                        if temp_accepts == 'e' or temp_complements == 'e' or temp_beginning_links == 'e':
                            return 'e', 'e', 'e'
                        #Accepting states stored
                        new_accepts = temp_accepts + new_accepts
                        #Complement states stored
                        new_comps   = temp_complements + new_comps
            else:
                #max_reps == 'n' -> sequence == {min_reps,} -> repeats # of min_reps, at least
                #Connect the latest accepting states from the latest instance of the sequence machine to the beginning of that instance of that machine
                #temp_accepts stores the accepting states of only the latest sequence machine built
                #temp_links stores the link-pairs of only the latest sequence machine built  
                if max_reps == 'n':
                    for pair in temp_beginning_links:
                        state = pair.state
                        link  = pair.link
                        destination = state.links[link]
                        for accept in temp_accepts:
                            accept.new_link(link, destination)
                #max_reps == 'm' -> sequence == {min_reps} -> repeats # of min_reps, stops
                #We're done here
                elif max_reps == 'm':
                    pass
                new_accepts = temp_accepts

            return new_accepts, new_comps, new_link

        machines_list = [char_sequence_machine, char_set_machine, in_range, star_machine, plus_machine, question_machine]
        return machines_list[target]

if __name__ == '__main__':

    # reg    = '[ab]'
    # string = 'cabcccabcabccccccaccb'
    # regex  = Regex(reg)
    # print(regex)
    # if not regex is None:
    #     print(regex.split(string))


    solving = True
    while solving:
        regex = input("Please enter the (single-line) regex you're checking against: ")
        reg   = Regex(regex)
        start = reg.generate_states(regex)
        # generate_states(regex)
        if not start is None:
            solving = False
        else:
            print('Try again!')
    solving = True
    while solving:
        print("Enter 'e' to quit.")
        print("Enter 'r' to create a new regex.")
        string = input("Please enter the (single-line) string to verify: ")
        if string == 'e':
            solving = False
            break
        elif string == 'r':
            while solving:
                regex = input("Please enter the (singel-line) regex you're checking against: ")
                reg   = Regex(regex)
                start = reg.generate_states(regex)
                if not start is None:
                    solving = False
                else:
                    print('Try again!')
            solving = True
        else:
            verified = reg.verify(start, string)
            if verified:
                print('\nCongratulation! Your string was accepted!\n')
            else:
                print('\nYour string was not accepted, try again!\n')
