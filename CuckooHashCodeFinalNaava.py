# I hereby certify that this program is solely the result of my own work and is
# in compliance with the Academic Integrity policy of the course syllabus and 
# the academic integrity policy of the CS department.


#import modules that will be needed
import random
import pytest

#import modules from BitHash.py
from BitHash import BitHash
from BitHash import ResetBitHash


class CuckooHash(object):
    
    # set up the basics of the class
    def __init__(self, size):
        
        # create two hash tables
        self.__hashTab1 = [None] * size 
        self.__hashTab2 = [None] * size
        self.__numKeys = 0        
        
        # get a seed for the hash functions to use
        # need to access these seeds in insert, delete, growHash, and find
        self.__seed1 = random.getrandbits(64)
        self.__seed2 = random.getrandbits(64) #use these in bitHash later on
        
        
        
    # return current number of keys in table    
    def __len__(self): return self.__numKeys   


    # Plan for what insert() will do:
    #  __insert: k, d, array1, array2
    #            if it succeeds, return None
    #            if it fails, it returns the last k,d that was evicted
    #
    #  grow_hash:
    #       create two larger arrays called a,b
    #       for each k,d in self.__hashtab1, invoke insert on k,d, a, b
    #       likewise for self.__hashtab2
    
    def insert(self, k, d):
        
        # don't allow inserting None   
        if k == None: return False        
        
        # check if the key has already been inserted:
        # note: the following code may seem reducndant when looking at __insert
        # below, but it's not since this runs less times than __insert does and
        # __insert keeps updating the k within the for loop, so it's different.
        
        # hash the key using first hash function
        hash1 = BitHash(k, self.__seed1)

        # get the position
        pos1 = hash1 % len(self.__hashTab1)  
        
        # check if it's in that position in the hash table, if so, just change 
        # the data by inserting it into the same position
        if self.__hashTab1[pos1] and k == self.__hashTab1[pos1][0]: 
            self.__hashTab1[pos1] = [k,d]                
            return None
        
        # second hash function, remember: just need the key when hashing
        hash2 = BitHash(k, self.__seed2)
        
        # get the position
        pos2 = hash2 % len(self.__hashTab2)

        #check if it's in that position in the hash table, if so, just change 
        #the data by inserting it into the same position        
        if self.__hashTab2[pos2] and k == self.__hashTab2[pos2][0]:
            self.__hashTab2[pos2] = [k,d]
            return None        
        
        # will get the key,data pair that was last unable to be inserted
        tryInsert = self.__insert(k, d, self.__hashTab1, self.__hashTab2)
        
        # if it succeeded, increment number of keys and return True
        # note: if self.__insert returns None, it means it worked
        if not tryInsert: 
            self.__numKeys +=1 
            return True
        
        # otherwise:
        #     growtable, reposition into the new places in the larger arrays
        #     use self.__insert again
        #     if it succeeds, return True
        #     otherwise raise an exception
        # use a loop so that it can keep trying different hash functions up to
        # 5 times, or until it succeeds
        # The reason the number 5 was chosen is because it doesn't always work
        # to only attempt to grow/reinsert everything once, but also can't have 
        # it get into an infinite loop. So 5, a small number, was chosen to 
        # allow it to have a few attempts of resetting bit Hash before simply
        # crashing.
        else:

            i = 0                       # set counter for looping
            growSucceeded = False       # set for loop to start
            
            # loop until grow and insert both succeed
            while not growSucceeded or tryInsert:

                # make new hash tables and inesrt k,d pairs into new tables
                growSucceeded = self.growHash()
                
                # if growing went well, then insert the last k,d pair that was
                # unable to be inserted - the reason for 'growing'/reseting the
                # hash function
                if growSucceeded:
                    tryInsert = self.__insert(tryInsert[0], tryInsert[1], self.__hashTab1, self.__hashTab2)

                i += 1          # increment to keep track of the loop
                
                # exit loop if it's tried too many times and is still failing
                if i == 5:
                    raise Exception("Failed to grow or insert properly")
                
            #update numKeys properly - if it successfully inserted
            self.__numKeys +=1 
               

          
    # The following __insert will be used by insert():      
    # returns None if did a successful insertion
    # if fails to insert
    # this will return k,d of last one that it couldn't insert
    def __insert(self, k, d, array1, array2):
        
        # save k,d into a variable to make looping easier
        cur2 = [k, d]


        # Loop until it seems to become 'infinite' - if can't find a home for a 
        # k,d pair so it keeps going back and forth. Then stop and resetBitHash
        # The size of the loop is not connected to the length of hash tables
        # to preserve good Big O.
        for i in range(50):
            # hash the key using first hash function
            hash1 = BitHash(cur2[0], self.__seed1)

            pos1 = hash1 % len(array1) # get the position

            # loop until you've successfully found a home for all key/data pairs
            # or it got into an "infinite loop"

            # use cur to keep track of what you're finding a home for - save value
            # from the end of the loop
            cur1 = array1[pos1]

            # stick new key/data pair into the position of first hash table that
            # it hashed to
            array1[pos1] = cur2
           
            # if position in first hash table was empty before you inserted
            # this k,d pair - it means you successfully inserted!
            if cur1 == None or cur1 == [None, None]: return None
            
            # if it wasn't empty, need to stick what was in it into the second
            # hash table. First hash it using second hash function
            
            # second hash function, remember: just need the key when hashing
            hash2 = BitHash(cur1[0], self.__seed2)
            
            pos2 = hash2 % len(array2)  # get new position

            # save what's in that position of second hash table
            cur2 = array2[pos2]

            # put cur1 - the key,data pair that was kicked out of first hash 
            # table - into the second hash table
            array2[pos2] = cur1
            
            # if cur2 was nothing, or the same key, return because you 
            # successfully inserted.
            # Otherwise, you will need to keep looping to try to find a home for
            # all key,data pairs            
            if cur2 == None or cur2 == [None, None]: return None   
                       
        # if reach here, it means you fell out of the loop and will need to 
        # rehash everything and grow the tables
        # So, return that last k,d that was evicted and couldn't find home for
        return cur2 
        
    def growHash(self):
        # Only grow the hash tables if they are getting too full, 
        # otherwise, this function just reinserts all the k,d pairs after 
        # resetting the hash function
        
        # note: nothing will change unless every k,d pair has a home 
        # since the arrays are only reassigned if all k,d pairs in old hash 
        # tables were successfully inserted. 
        
        # calculate what size to make the new arrays
        if len(self.__hashTab1) < (self.__numKeys * 2):
            size = len(self.__hashTab1)*2
        else:
            size = len(self.__hashTab1)
            
        # create two new arrays
        a = [None]*size
        b = [None]*size
        
        # reset bit hash each time you invoke growHash to help spread out each 
        # k,d pair and avoid collisions
        ResetBitHash()  
        
        # for each k,d in the hash tables, invoke insert on k,d, a, b
        # if fails to insert into the new tables, then return False
        # start by going through the first hash table
        for i in range(len(self.__hashTab1)):
           # nothing needs to be done if it's an empty spot
            if self.__hashTab1[i] == None:
                continue
                
            else:
                # if there is something in that spot, get the key and data
                key = self.__hashTab1[i][0]
                data = self.__hashTab1[i][1] 
                
                # Try to insert that k,d pair into the new tables
                # returns None if works, returns key, data pair if doesn't work
                firstIn = self.__insert(key, data, a, b)
                
                # no point in going further if it didn't work, so return to get out 
                # of this function and it will either try to reset bitHash, etc. or 
                # the whole thing will crash since it can't insert after trying to 
                #grow and reset the hash
                if firstIn != None:
                    return False
            
        # now go through the second hash table and try to insert into new tables    
        for j in range(len(self.__hashTab2)):
            
            # if that place in array was empty, nothing needs to be inserted
            if self.__hashTab2[j] is None:  
                continue
            
            # if there was something in the array, 
            else:
                # get the key,data pair that was there
                key2 = self.__hashTab2[j][0]
                
                data2 = self.__hashTab2[j][1]            
            
            # try to insert that k,d pair into the new tables
            secIn = self.__insert(key2, data2, a, b)
            
            #if the insert failed, return False
            if secIn != None:
                return False
       
        # if all inserts were successful, reassign the new tables:
        self.__hashTab1 = a 
        self.__hashTab2 = b      
        
        # this means it was successful and each k,d pair has a home
        return True
    
    # Find - The general plan:
    # hash the key, check if in first table. If not, check if in second table. 
    # rehash the key using second hashfunction in order to check if in second table.
    # return when/if found
    # if not in either table, it's not there.
    def find(self, k):
        # hash the key using first hash function
        hash1 = BitHash(k, self.__seed1)
        
        # get the position it would be in
        pos = hash1 % len(self.__hashTab1)
        
        # check if it's in the first hashtable in that position
        if self.__hashTab1[pos] and self.__hashTab1[pos][0] == k:
            # if so, return k,d pair that it found
            return self.__hashTab1[pos]
        
        # if it's not in first table, check in second table
        # first hash using second hash function
        hash2 = BitHash(k, self.__seed2)
        
        # get the position it would be in
        pos2 = hash2 % len(self.__hashTab2)    
        
        # if it's in the corresponding position in second hash table,
        # return k,d
        if self.__hashTab2[pos2] and self.__hashTab2[pos2][0] == k: 
            return self.__hashTab2[pos2] #return key,data pair that was found
        
        # if got here, it's not in either table
        else: return None
        
    # Delete: use similar method to find in order to know where it is 
    # if found, empty that cell
    def delete(self, k):
        # hash the key using first hash function
        hash1 = BitHash(k, self.__seed1)
        
        # get the position it would be in
        pos = hash1 % len(self.__hashTab1)
        
        # check if it's in the first hashtable in that position
        if self.__hashTab1[pos] and self.__hashTab1[pos][0] == k: 
            # if so, set that key,data pair to be None
            self.__hashTab1[pos] = None 
            
            #decrement the number of keys that are in the tables
            self.__numKeys -=1
            # return upon successful deletion
            return True
        
        # if it's not in first table, check in second table
        # first hash using second hash function
        hash2 = BitHash(k, self.__seed2)
        
        # get the position it would be in
        pos2 = hash2 % len(self.__hashTab2)    
        
        # check if it's in that position
        if self.__hashTab2[pos2] and self.__hashTab2[pos2][0] == k: 
            # if so, set that key,data pair to be None
            self.__hashTab2[pos2] = None 
            
            #decrement the number of keys that are in the tables
            self.__numKeys -=1
           
            # return upon successful deletion
            return True
        
        # if got here, it's not in either table
        else: return False        
        
    # to help see what the hash tables look like    
    def display(self):
        #loop through the first hash array printing out the k,d pairs
        for i in range(len(self.__hashTab1)):
            print(self.__hashTab1[i], "; ", end = "")
        
        #put space in between the two hash arrays for aesthetic purposes
        print() 
        
        #now loop through the second hash array printing out the k,d pairs
        for j in range(len(self.__hashTab2)):
            print(self.__hashTab2[j], "; ", end = "")
            
    # utility function to be used by pytests to check if all keys are in the 
    # right positions. This is similar to find, but doing it for every single key
    def isCuckoo(self):
        ans = False
        
        # loop through the whole first array, 
        # for each k,d pair in i'th position, compute what bucket the key should
        # be in and check that it's in that bucket 
        # (just like find - might need to check both arrays)
        
        for i in range(len(self.__hashTab1)):
            
            # if there's a none in that position, just continue - don't check it
            if not self.__hashTab1[i]: continue 
            
            # get the key,data pair
            k, d = self.__hashTab1[i]
            
            #compute that corrseponding hash function
            hashF = BitHash(k, self.__seed1)
            
            # get the position it would be in
            pos = hashF % len(self.__hashTab1)
            
            # check if that key,data pair were in the right position
            if i == pos: ans = True
            
            # return false right away if anything isn't true, because it means 
            # it failed
            else: return False 
        
        # now check the k,d pairs in the second hash table    
        for i in range(len(self.__hashTab2)):
            
            # if there's a none in that position, just continue - don't check it
            if not self.__hashTab2[i]: continue 
            
            # get the key,data pair in that position
            k, d = self.__hashTab2[i]
            
            # compute the hash function for it
            hashF = BitHash(k, self.__seed2)
            
            # get the position it would be in
            pos = hashF % len(self.__hashTab2)
            
            # check if that key,data pair were in the right position
            if i == pos: ans = True
            
            # return false right away if anything isn't true, because it means 
            # it failed
            else: return False         
        
        # If get here, it means it's all in the right positions    
        if ans != False: return True
        


# Pytests:

# Make sure there are the right amount of k,d pairs in the tables            
def test_numKeys():
    h = CuckooHash(10)
    
    # insert some k,d pairs
    h.insert("Hello", 1)
    h.insert("there", 2)
    h.insert("test", 3)
    
    assert len(h) == 3
    
# check that numKeys is doing the right thing            
def test_numKeysLarge():
    h = CuckooHash(100000)
    
    # insert many k,d pairs
    for i in range(1000):
        h.insert(str(i), i)
   
   #check the amount of keys
    assert len(h) == 1000

# check that the find function works in that it only finds keys you inserted    
def test_findNo():
    h = CuckooHash(10)
    
    # insert some k,d pairs
    h.insert("Hello", 1)
    h.insert("there", 2)
    h.insert("test", 3)
    
    assert h.find("Hi") == None

# Test find and insert: check that the key you inserted is really there     
def test_findYes():
    h = CuckooHash(10)
    
    # insert some k,d pairs
    h.insert("Hello", 1)
    h.insert("there", 2)
    h.insert("test", 3)
    
    assert h.find("Hello") == ["Hello", 1]
    
def test_find2():
    h = CuckooHash(10)
    
    # insert some k,d pairs
    h.insert("When", 1)
    h.insert("will", 2)
    h.insert("we", 3)
    h.insert("be", 6)
    h.insert("there", 4)
   
    assert h.find("will") == ["will", 2]


# Check what happens when insert the same key more than once    
def test_insertAgain():
    h = CuckooHash(10)
    
    # insert some k,d pairs
    h.insert("When", 1)
    h.insert("will", 2)
    h.insert("we", 3)
    h.insert("be", 6)
    h.insert("there", 4)
    
   # try inserting the same key again (a few times) but with dif data 
    h.insert("will", 5)
    h.insert("will", 1)
    h.insert("will", 55)
    
    #now see which k,d pair it will find. It should find the last one inserted    
    assert h.find("will") == ["will", 55]
    
    
def test_insertAgainNotFound():
    h = CuckooHash(10)
    
    # insert some k,d pairs
    h.insert("When", 1)
    h.insert("will", 2)
    h.insert("we", 3)
    h.insert("be", 6)
    h.insert("there", 4)
    
   # try inserting same key again (a few times) and see what happens
    h.insert("will", 5)
    h.insert("will", 1)
    h.insert("will", 55)
    
    # check that the data is updated by seeing that the data returned by the find 
    # function is not the same as a data that was inserted earlier with that 
    # same key
    assert h.find("will") != ["will", 1]
    
# insert all the same exact k,d pairs    
def test_insertAgain2():
    h = CuckooHash(10)
    for i in range(4):
        h.insert(chr(i + ord('A')), i)
        
   # try inserting the same exact keys again and see what happens
    for i in range(4):
        h.insert(chr(i + ord('A')), i)
    assert h.isCuckoo() == True
    
# test both grow and insert functions by inserting the full amount
# and then doing the same exact insert again
def test_reinsertAndGrow():
    h = CuckooHash(10)
   
    # insert key,data pairs    
    for i in range(10):
        h.insert(chr(i + ord('A')), i)
        
    #get the amount of keys you've inserted so far    
    size = len(h)
        
   # try inserting same keys again and see what happens
    for j in range(10):
        h.insert(chr(j + ord('A')), i)
        
    #get the amount of keys that are in there now     
    size2 = len(h)   
    
    # did it properly insert and not allow doubles?
    # test it by seeing if the sizes are the same - they should be since don't
    # allow doubles and don't increment unless insert a new key
    assert size2 == size
    
    #check if it's a proper cuckoo hash object
    assert h.isCuckoo() == True
    
# Check that the delete function works 
def test_delete():
    h = CuckooHash(10)
    
    # insert a few key,data pairs
    for i in range(9):
        h.insert(str(i), i)
        
   #check that basic delete works
    assert h.delete('4') == True

def test_delete2():
    h = CuckooHash(10)
    

    # insert a few key,data pairs    
    h.insert("When", 1)
    h.insert("will", 2)
    h.insert("we", 3)
    h.insert("be", 6)
    h.insert("there", 4)
   
    assert h.delete("we") == True
    
def test_deleteNone():
    h = CuckooHash(10)

    # insert key,data pairs    
    for i in range(9):
        h.insert(str(i), i)
    
    # can't delete since never put in a None key    
    assert h.delete(None) == False 
    
    
#more intense tests to check that delete really works

#delete everything
def test_deleteAll():
    h = CuckooHash(10)
        
    # initialize a dictionary to keep track of all k,d pairs that were inserted
    dictK = dict()
    
    #insert some k,d pairs and each time, add the key,data to dict as well
    for i in range(7):
        key = str(random.random())
        h.insert(key, i)
        
        dictK[key] = i 
    
    # now try to delete all the keys and check if the arrays 'empty' out
    
    # loop through the dictionary
    for k in dictK:
        
        # get what the data should be
        data = dictK[k]
        
        #delete that k,d pair
        deleted = h.delete(k)
        
        #check if delete works
        if deleted == False: assert False
    
    #if made it here, it means that all the deletes were successful
    #now check that the whole thing is empty
    assert len(h) == 0
        
#test delete and find at the same time
#making sure it can't find a key that was already deleted
def test_deletedNotThere():
    #initialize the cuckoo hash array object
    h = CuckooHash(10)
    
    #insert a few k,d pairs
    h.insert("When", 1)
    h.insert("will", 2)
    h.insert("we", 3)
    h.insert("be", 6)
    h.insert("there", 4)
   
    # delete an item
    h.delete("be")
    
    #make sure 'find' can't find that deleted item
    assert h.find("be") == None

# use isCuckoo function to test if all the keys are in the right positions    
def test_isCuck():
    h = CuckooHash(10)

    # insert a few key,data pairs    
    h.insert("When", 1)
    h.insert("will", 2)
    h.insert("we", 3)
    h.insert("be", 6)
    h.insert("there", 4)
    
    assert h.isCuckoo() == True
    
# testing to make sure all keys are in right position 
# (again, but using more keys this time, and no 'None' values)
def test_isItCuckoo():
    h = CuckooHash(100000)
    
    # insert many k,d pairs
    for i in range(1000):
        h.insert(str(random.random()), i)
   
    # check if it worked
    assert h.isCuckoo() == True

# Even larger!
def test_isItCuckooHuge():
    h = CuckooHash(10000)
    
    #insert many k,d pairs
    for i in range(60000):
        h.insert(str(random.random()), i)
    
    #check if it worked
    assert h.isCuckoo() == True


# Check that you can't add a None by checking how many keys are in the table 
# after trying to add a none   
def test_noneLen():
    h = CuckooHash(10)
    
    # insert a few k,d pairs
    h.insert("When", 1)
    h.insert("will", 2)
    h.insert("we", 3)
    h.insert("be", 6)
    h.insert(None, None)
    
    # check that trying to insert none didn't change the amount of keys in table
    assert len(h) == 4

# checking that you can't add a none by using insert    
def test_insertNone():
    h = CuckooHash(10)
    
    # insert a few k,d pairs
    h.insert("When", 1)
    h.insert("will", 2)
    h.insert("we", 3)
    h.insert("be", 6)
    
    #check that it doesn't let you insert a None
    assert h.insert(None, None) == False

# Again, checking that you can't add a none by using insert but also having a 
# data amount that's not None
def test_insertNone2():
    h = CuckooHash(10)
    
    # insert a few k,d pairs
    h.insert("When", 1)
    h.insert("will", 2)
    h.insert("we", 3)
    h.insert("be", 6)
    
    #check that it doesn't let you insert a None, even with a real data pair
    assert h.insert(None, 9) == False
    
# Use isCuckoo again, and make sure you can't add a None    
def test_isCuckNone():
    h = CuckooHash(10)
    
    # insert a few key,data pairs
    h.insert("When", 1)
    h.insert("will", 2)
    h.insert("we", 3)
    h.insert("be", 6)
    h.insert(None, None)
    
    assert h.isCuckoo() == True
    
# test the growHash function by invoking a small cuckoo hash and adding many 
# more keys to it; forcing it to grow    
def test_growSmall():
    h = CuckooHash(2)
    
    #insert a few k,d pairs - enough that the hash tables will have to grow
    h.insert("Today", 1)
    h.insert("is", 2)    
    h.insert("a", 3)
    h.insert("great", 6)
    h.insert("day", 10)
    
    
    #check if it worked
    assert h.isCuckoo() == True


# test grow Hash again - this time on a bigger scale
def test_growing():
    h = CuckooHash(10)
    
    #insert many random k,d pairs
    for i in range(1000):
        h.insert(str(random.random()), i)
        
    #check if it worked    
    assert h.isCuckoo() == True
    
#check for all the keys that were inserted
def test_allKeys():
    h = CuckooHash(10000)
    
    # initialize a set to keep track of all keys that were inserted
    setK = set()
    
    # initialize variable to know if any keys are missing from the tables
    # set it to be True since will only have it turn False if find can't find it
    allThere = True
    
    # loop to insert 1000 keys into the hash arrays
    for i in range(1000):
        key = str(random.random())
        h.insert(key, i)
        setK.add(key)
        
    # now check that all the keys that you tried to insert actually got inserted
    for element in setK:
        if h.find(element) == False: return False
    
    # if you got through the whole set of keys and allThere is still true, it 
    # means that all the keys were found to be there
            
    assert allThere == True

#check that all key,data pairs that were inserted can be found in the tabels
def test_allKeysAndData():
    h = CuckooHash(10000)
    
    # initialize a dictionary to keep track of all k,d pairs that were inserted
    dictK = dict()
    
    # initialize variable to know if any keys are missing from the tables
    # set it to be True since will only have it turn False if find can't find it
    allThere = True
    
    # loop to insert 1000 keys into the hash arrays
    for i in range(1000):
        key = str(random.random())
        h.insert(key, i)
        dictK[key] = i
        
    # now check that all the keys that you tried to insert actually got inserted
    for k in dictK:
        data = dictK[k]  #get what the data should be
        
        #check if the key matches the right data
        if h.find(k) == [k, data]: allThere = True
        
        #have the test fail immediately if it can't find the correct k,d pair
        else: assert False 
    
    # if you got through the whole set of keys and allThere is still true, it 
    # means that all the keys were found to be there  
    assert allThere == True
    
    
def test_keyDataKnown():
    h = CuckooHash(10)
    
    # initialize a dictionary to keep track of all k,d pairs that were inserted
    dictK = dict()
    
    # initialize variable to know if any keys are missing from the tables
    # set it to be True since will only have it turn False if find can't find it
    allThere = True
    
    # insert some k,d pairs into the hash array
    # add then add that k,d pair, that was just inserted, into the dict
    h.insert("Lions", 2)
    dictK["Lions"] = 2
    
    h.insert("tree", 1)
    dictK["tree"] = 1  
    
    h.insert("eyes", 2)
    dictK["eyes"] = 2
    
    h.insert("toes", 10)
    dictK["toes"] = 10
        
    # now check that the keys that you tried to insert actually got inserted
    for k in dictK:
        data = dictK[k]  #get what the data should be
        
        #check if the key matches the right data
        if h.find(k) == [k, data]: allThere = True
        
        #have the test fail immediately if it can't find the correct k,d pair
        else: assert False     
   
    # if you got through the whole set of keys and allThere is still true, it 
    # means that all the keys were found to be there
            
    assert allThere == True
      
pytest.main(["-v", "-s", "CuckooHashCodeFinalNaava.py"])
