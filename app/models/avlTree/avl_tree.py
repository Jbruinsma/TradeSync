from app.models.avlTree.avl_node import AVLNode
import json
import pickle

class AVLTree:

    def __init__(self):
        self.root = None
        self.observers = []

    def add_observer(self, observer):
        self.observers.append(observer)

    def remove_observer(self, observer):
        self.observers.remove(observer)
        
    def notify_observers(self):
        for observer in self.observers:
            observer.update()

    def insert(self, key, val):
        """
        Inserts a key-value pair into the tree.
        Returns True if successful, False if key already exists.
        """
        if key is None:
            raise ValueError("Key cannot be None")
        if self.contains(key):
            return False
        self.root = self._insert(self.root, key, val)
        self.notify_observers()
        return True

    def delete(self, key):
        self.root = self._delete(self.root, key)
        self.notify_observers()

    def search(self, key):
        return self._search(self.root, key)

    def contains(self, key):
        return self._search(self.root, key) is not None

    def update(self, key, val):
        node = self._search(self.root, key)
        if node is None:
            return False
        node.val = val
        self.notify_observers()
        return True
    
    def inorder_traversal(self):
        return self._inorder_traversal(self.root)

    def _insert(self, node, key, val):
        if node is None: return AVLNode(key, val)
        if key < node.key: node.left = self._insert(node.left, key, val)
        elif key > node.key: node.right = self._insert(node.right, key, val)
        else: return node 
        node.height = 1 + max(self._get_height(node.left), self._get_height(node.right))  
        balance = self._get_balance(node)   
        if balance > 1 and key < node.left.key: return self._right_rotate(node)  
        if balance < -1 and key > node.right.key: return self._left_rotate(node) 
        if balance > 1 and key > node.left.key:
            node.left = self._left_rotate(node.left)
            return self._right_rotate(node) 
        if balance < -1 and key < node.right.key:
            node.right = self._right_rotate(node.right)
            return self._left_rotate(node)
        return node

    def _delete(self, node, key):
        if node is None:
            return node
        if key < node.key:
            node.left = self._delete(node.left, key)
        elif key > node.key:
            node.right = self._delete(node.right, key)
        else:
            if node.left is None:
                temp = node.right
                node = None
                return temp
            elif node.right is None:
                temp = node.left
                node = None
                return temp
            temp = self._get_min_value_node(node.right)
            node.key = temp.key
            node.val = temp.val
            node.right = self._delete(node.right, temp.key)
        if node is None:
            return node
        node.height = 1 + max(self._get_height(node.left), self._get_height(node.right))
        balance = self._get_balance(node)
        if balance > 1 and self._get_balance(node.left) >= 0:
            return self._right_rotate(node)
        if balance > 1 and self._get_balance(node.left) < 0:
            node.left = self._left_rotate(node.left)
            return self._right_rotate(node)
        if balance < -1 and self._get_balance(node.right) <= 0:
            return self._left_rotate(node)
        if balance < -1 and self._get_balance(node.right) > 0:
            node.right = self._right_rotate(node.right)
            return self._left_rotate(node)
        return node

    def _search(self, node, key):
        if node is None or node.key == key:
            return node
        if key < node.key:
            return self._search(node.left, key)
        return self._search(node.right, key)

    def _get_balance(self, node):
        if node is None:
            return 0
        return self._get_height(node.left) - self._get_height(node.right)

    @staticmethod
    def _get_height(node):
        if node is None:
            return 0
        return node.height

    def _left_rotate(self, node):
        new_root = node.right
        temp = new_root.left
        new_root.left = node
        node.right = temp
        node.height = 1 + max(self._get_height(node.left), self._get_height(node.right))
        new_root.height = 1 + max(self._get_height(new_root.left), self._get_height(new_root.right))
        return new_root

    def _right_rotate(self, node):
        new_root = node.left
        temp = new_root.right
        new_root.right = node
        node.left = temp
        node.height = 1 + max(self._get_height(node.left), self._get_height(node.right))
        new_root.height = 1 + max(self._get_height(new_root.left), self._get_height(new_root.right))
        return new_root

    def _preorder_traversal(self, node):
        if node is None:
            return []
        return [node.key] + self._preorder_traversal(node.left) + self._preorder_traversal(node.right)

    def _inorder_traversal(self, node):
        if node is None:
            return []
        return self._inorder_traversal(node.left) + [node.val] + self._inorder_traversal(node.right)

    def _postorder_traversal(self, node):
        if node is None:
            return []
        return self._postorder_traversal(node.left) + self._postorder_traversal(node.right) + [node.key]

    def find_account(self, account_id):
        return self._find_account(self.root, account_id)

    def _find_account(self, node, account_id):
        if node is None:
            return None

        left_result = self._find_account(node.left, account_id)
        if left_result:
            return left_result

        if account_id in node.val.master_accounts:
            return node.val.master_accounts[account_id]
        for master_account in node.val.master_accounts.values():
            if account_id in master_account.child_account_ids:
                return master_account.child_accounts[account_id]

        return self._find_account(node.right, account_id)

    def is_empty(self):
        return self.root is None

    @staticmethod
    def _get_min_value_node(node):
        current = node
        while current.left is not None:
            current = current.left
        return current

    def save_to_file(self, filename):
        """Saves the tree to a file"""
        try:
            with open(filename, 'wb') as f:
                pickle.dump(self.root, f)
            return True
        except Exception as e:
            print(f"Error saving tree: {e}")
            return False

    def load_from_file(self, filename):
        """Loads the tree from a file"""
        try:
            with open(filename, 'rb') as f:
                self.root = pickle.load(f)
            return True
        except Exception as e:
            print(f"Error loading tree: {e}")
            return False
