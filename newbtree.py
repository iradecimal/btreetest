from math import floor, ceil
# Searching a key on a B-tree in Python

traversals = 0
comparisons = 0

# Create a node
class BTreeNode:
    def __init__(self, leaf=False):
        self.leaf = leaf
        self.keys = []
        self.child = []
        
# Tree       
class BTree:
    
    def __init__(self, m):
        self.root = BTreeNode(True) #creates a root node with no keys
        self.m = m
        self.minkeys = floor(m/2)
        self.maxkeys = m-1
    # Insert a key
    
    def search(self, node, key):
        global traversals, comparisons
        traversals += 1
        i = 0
        while i < len(node.keys) and key > node.keys[i][0]:
            comparisons += 1
            i += 1
        if i < len(node.keys) and key == node.keys[i][0]:
            return(node.keys[i])
        if node.leaf:
            return
        return self.search(node.child[i], key) # type: ignore

    def insert_key(self, key):
        r = self.root
        #check if the root's key are full
        if len(self.root.keys) >= self.maxkeys:
            #create a new root node, then split and insert the key
            temp = BTreeNode()
            self.root = temp
            temp.child.insert(0, r)
            self.split_child(temp, 0)
            self.insert_nonfull(temp, key)
        else:
            self.insert_nonfull(r, key)

    #recursive function for insertion
    def insert_nonfull(self, node, key):
        global traversals, comparisons
        
        traversals += 1
        i = len(node.keys) - 1
        if node.leaf:
            #find where the new key will belong within the node's list of keys
            node.keys.append((None, None)) #create an empty node 
            while i >= 0 and key[0] < node.keys[i][0]:
                comparisons += 1
                node.keys[i+1] = node.keys[i]
                i -= 1
            #insert the new key within the list at the specified position
            node.keys[i+1] = key
        else: #node is not a leaf
            #find where the new key will belong within the node's list of keys
            while i >= 0 and key < node.keys[i]:
                comparisons += 1
                i -= 1
            #increment the counter to point towards the right-hand side
            i += 1
            #if the child isn't full, insert it there, if not, split then insert
            if len(node.child[i].keys) >= self.maxkeys:
                self.split_child(node, i)
                if key[0] > node.keys[i][0]:
                    i += 1
            self.insert_nonfull(node.child[i], key)
    
    #pass both the praent node and the child in which the split would occur
    def split_child(self, node, i):
        #store the node's child in y
        y = node.child[i]

        #create a new node which will be new if the old node's child was
        z = BTreeNode(y.leaf)
        #insert the new node into the children of the parent node
        node.child.insert(i+1, z)
        #insert the middle key of y to the parent node
        node.keys.insert(i, y.keys[self.minkeys-1])

        #assign the first half of keys to y, second half to z
        z.keys = y.keys[self.minkeys: self.maxkeys]
        y.keys = y.keys[0: self.minkeys-1]

        if not y.leaf: #do the same for its children if it's not a leaf
            z.child = y.child[self.minkeys: (2*self.minkeys)]
            y.child = y.child[0: self.minkeys]

    def delete(self, node, key):
        global comparisons
        i = 0
        while i < len(node.keys) and key[0] > node.keys[i][0]:
            comparisons += 1
            i += 1
        if node.leaf: 
            #Case 1: Node is a leaf
            #confirm that key was found and pop it
            if i < len(node.keys) and key[0] == node.keys[i][0]:
                node.keys.pop(i)
                return
        else:
            #Case 2: Key is found in an internal node:
            if i < len(node.keys) and key[0] == node.keys[i][0]:
                return self.delete_internal_node(node, key, i)
            #Case 3: Key is not in node, go to the proper child
            if len(node.child[i].keys) < self.minkeys:
                self.borrow(node, i)
            self.delete(node.child[i], key)

    def delete_internal_node(self, node, key, i):
        #Case 2a: left-side child (predecessor) has enough keys
        if len(node.child[i].keys) >= self.minkeys:
            pred_key = self.get_predecessor(node, i)
            node.keys[i] = pred_key
            self.delete(node.child[i], pred_key)
        #Case 2b: right-side child (successor) has enough keys
        elif len(node.child[i+1].keys) >= self.minkeys:
            succ_key = self.get_successor(node, i)
            node.keys[i] = succ_key
            self.delete(node.child[i], succ_key)
        #Case 2c: both sides don't have enough keys
        else:
            self.merge(node, i)
            self.delete(node.child[i], key)

    def get_predecessor(self, node, i):
        curr = node.child[i]
        while not curr.leaf:
            curr = curr.child[len(curr.child) - 1]
        return curr.keys[len(curr.keys) - 1]
    
    def get_successor(self, node, i):
        curr = node.child[i]
        while not curr.leaf:
            curr = curr.child[0]
        return curr.keys[0]

    #merge function to merge two children into child
    def merge(self, node, i):
        child = node.child[i]
        sibling = node.child[i + 1]
        #merge key from node to child
        child.keys.append(node.keys[i])
        #append sibling's keys to child
        child.keys.extend(sibling.keys)

        #if the sibling has children, append them to child (remember properties of B-Tree)
        if not child.leaf: 
            child.child.extend(sibling.child)

        #remove the key from node, delete sibling for child list
        node.keys.pop(i)
        node.child.pop(i+1)

        #if the root becomes empty, reduce the height of the tree
        if len(node.keys) == 0:
            self.root = child

    #helper function to fill a child with at least minkeys(m/2) keys
    def borrow(self, node, i):
        #borrow from the left/previous sibling
        if i != 0 and len(node.child[i-1].keys) >= self.minkeys:
            self.borrow_from_prev(node, i)
        #borrow from the right/next sibling
        if i != len(node.child) - 1 and len(node.child[i+1].keys) >= self.minkeys:
            self.borrow_from_next(node, i)
        #both siblings are too small
        else:
            #check if there is a next sibling to merge with (or use the prev instead) 
            if i != len(node.child) - 1:
                self.merge(node, i)
            else:
                self.merge(node, i-1)
        
    
    def borrow_from_prev(self, node, i):
        child = node.child[i]
        sibling = node.child[i - 1]
        # Move the last key from sibling to node
        child.keys.insert(0, node.keys[i - 1])
        node.keys[i - 1] = sibling.keys.pop()
        #if both are not leaves move the last child of sibling to child
        if not child.leaf:
            child.child.insert(0, sibling.child.pop())
            
    def borrow_from_next(self, node, i):
        child = node.child[i]
        sibling = node.child[i + 1]
        # Move the first key from sibling to node
        child.keys.append(node.keys[i])
        node.keys[i] = sibling.keys.pop(0)
        #if both are not leaves ove the first child of sibling to child if sibling
        if not child.leaf:
            child.child.append(sibling.child.pop(0))


    # Print the tree
    def print_tree(self, x, l=0):
        print("Level ", l, " ", len(x.keys), end=":")
        for i in x.keys:
            print(i, end=" ")
        print()
        l += 1
        if len(x.child) > 0:
            for i in x.child:
                self.print_tree(i, l)

B = BTree(4)
# for i in range(4):
#     B.insert_key((i, chr(i + 65)))
# print()
# B.print_tree(B.root)
# B.delete(B.root, (3,))
# B.print_tree(B.root)
        
for i in range(12):
    B.insert_key((i, chr(i + 65)))
B.print_tree(B.root)
B.search(B.root, 5)
B.delete(B.root, (8,))
B.delete(B.root, (0,))
B.delete(B.root, (9,))
print("\n")
B.print_tree(B.root)
B.insert_key((12, chr(11 + 65)))
B.insert_key((13, chr(13 + 65)))
print("\n")
B.print_tree(B.root)
B.insert_key((12, chr(11 + 65)))
B.insert_key((0, chr(0 + 65)))
print("\n")
B.print_tree(B.root)

