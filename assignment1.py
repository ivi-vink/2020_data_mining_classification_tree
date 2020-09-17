import time
import numpy as np

credit_data = np.genfromtxt('./credit_score.txt',
                            delimiter=',',
                            skip_header=True)

# age,married,house,income,gender,class
# [(22, 0, 0, 28, 1, 0)
#  (46, 0, 1, 32, 0, 0)
#  (24, 1, 1, 24, 1, 0)
#  (25, 0, 0, 27, 1, 0)
#  (29, 1, 1, 32, 0, 0)
#  (45, 1, 1, 30, 0, 1)
#  (63, 1, 1, 58, 1, 1)
#  (36, 1, 0, 52, 1, 1)
#  (23, 0, 1, 40, 0, 1)
#  (50, 1, 1, 28, 0, 1)]

# In the program data points are called rows

# In the program categorical or numerical attributes are called cols for columns

# The last column are the classes and will be called as classes in the program


class Node:
    """
    The node object points to two other Node objects.
    """
    def __init__(self, split_value_or_rows=None, col=None):
        """Initialises the column and split value for the node.

        /split_value_or_rows=None/ can either be the best split value of
        a col, or a boolean mask for x that selects the rows to consider for
        calculating the split_value

        /col=None/ if the node object has a split_value, then it also has a col
        that belongs to this value

        """
        self.split_value_or_rows = split_value_or_rows
        self.col = col

    def add_split(self, left, right):
        """
        Method that is called in the main loop of tree_grow.

        Lets the node object point to two other objects that can be either Leaf
        or Node.
        """
        self.left = left
        self.right = right

    def is_leaf_node(self, node_classes):
        """
        @todo: Docstring for is_leaf_node
        """
        self.col = None
        self.split_value_or_rows = np.argmax(
            np.bincount(node_classes.astype(int)))


# class Leaf:
#     """
#     Simple class that contains only the majority class in the leaf node.
#     """
#     def __init__(self, maj_class):
#         """Initialises the majority vote.

#         /maj_class/ @todo

#         """


class Tree:
    """
    Tree object that points towards the root node.
    """
    def __init__(self, root_node_obj):
        """Initialises only by pointing to a Node object.

        /root_node_obj/ is a node object that is made before entering the main
        loop of tree grow.

        """
        self.tree = root_node_obj

    # def __repr__(self):
    #     nodelist = [self.tree]
    #     tree_str = ''
    #     while nodelist:
    #         current_node = nodelist.pop()
    #         # print(current_node.value)
    #         try:
    #             childs = [current_node.right, current_node.left]
    #             nodelist += childs
    #         except AttributeError:
    #             pass
    #         col, c = current_node.value
    #         tree_str += f"{col=}, {c=}"
    #     return tree_str


def impurity(array) -> int:
    """
    Assumes the argument array is a one dimensional vector of zeroes and ones.
    Computes the gini index impurity based on the relative frequency of ones in
    the vector.

    Example:

    >>> array=np.array([1,0,1,1,1,0,0,1,1,0,1])
    >>> array
    array([1,0,1,1,1,0,0,1,1,0,1])

    >>> impurity(array)
    0.23140495867768596
    """
    # Total labels
    n_labels = len(array)
    if n_labels == 0:
        print(
            "division by zero will happen, child node is pure, doesnt contain anything"
        )
        n_labels = 1
    # Number of tuples labeled 1
    n_labels_1 = array.sum()
    # Calculate the relative frequency of ones with respect to the total labels
    rel_freq_1 = n_labels_1 / n_labels
    # Use the symmetry around the median property to also calculate the
    # relative frequency of zeroes
    rel_freq_0 = 1 - rel_freq_1
    # Multiply the frequencies to get the gini index
    gini_index = rel_freq_1 * rel_freq_0
    return gini_index


def bestsplit(x, y, min_leaf) -> None:
    """
    x = vector of single col
    y = vector of classes (last col in x)

    Consider splits of type "x <= c" where "c" is the average of two consecutive
    values of x in the sorted order.

    x and y must be of the same length

    y[i] must be the class label of the i-th observation, and x[i] is the
    correspnding value of attribute x

    Example (best split on income):

    >>> bestsplit(credit_data[:,3],credit_data[:,5])
     36
    """
    x_sorted = np.sort(np.unique(x))
    if len(x_sorted) <= 2:
        # Allows splitting on categorical (0 or 1) cols
        split_points = x_sorted / 2
    else:
        # Take average between consecutive numerical rows in the x col
        split_points = (x_sorted[:len(x_sorted) - 1] + x_sorted[1:]) / 2

    # De toepassing van bestsplit verdeelt de x col vector in tweeen, twee
    # arrays van "x rows". Deze moeten we terug krijgen om de in de child nodes
    # bestsplit toe te passen.
    #
    # Deze lus berekent de best split value, en op basis daarvan weten we welke
    # twee "x rows" arrays we moeten returnen, en welke split value het beste
    # was natuurlijk.

    # Nodig voor de delta i formule
    impurity_parent, n_rows_parent = impurity(y), len(y)

    # Hieren stoppen we (delta_i, split_value, rows_left, rows_right)
    best_list = []
    # Stop wanneer de array met split points leeg is
    while split_points.size != 0:
        # Huidige split value
        split_value = split_points[-1]
        # boolean masks om x rows mee te masken/slicen
        mask_left, mask_right = x > split_value, x <= split_value

        # class voor beide split kanten
        classes_left, classes_right = y[mask_left], y[mask_right]

        # Kijk of er genoeg rows in de gesplitte nodes terechtkomen, anders
        # mogen we de split niet toelaten vanwege de min_leaf constraint
        if len(classes_left) < min_leaf or len(classes_right) < min_leaf:
            # Haal de huidige split_point uit split_points
            split_points = split_points[:-1]
            continue

        # delta_i formule
        delta_i = impurity_parent - (
            impurity(classes_left) * len(classes_left) +
            impurity(classes_right) * len(classes_right)) / n_rows_parent
        # stop huidige splits in de lijst om best split te berekenen
        best_list.append((delta_i, mask_left, mask_right, split_value))
        # Haal de huidige split_point uit split_points
        split_points = split_points[:-1]
    # Bereken de best split voor deze x col
    return max(best_list, key=lambda x: x[0])


def exhaustive_split_search(rows, classes, min_leaf):
    """
    @todo: Docstring for exhaustive_split_search
    """
    # We hebben enumerate nodig, want we willen weten op welke col
    # (age,married,house,income,gender) we een split doen
    exhaustive_best_list = []
    # print(f"{rows=}, {classes=}")
    for i, col in enumerate(rows.transpose()):
        # calculate the best split for the col that satisfies the min_leaf
        # constraint
        col_best_split = bestsplit(col, classes, min_leaf)
        # add for which row we calculated the best split
        col_best_split += (i,)
        exhaustive_best_list.append(col_best_split)
    return exhaustive_best_list

def add_children(node, x, best_split):
    """
    @todo: Docstring for add_children
    """
    # The mask that was used to get the rows for the current node from x, we
    # need this to update the rows for the children
    current_mask = node.split_value_or_rows

    # Unpacking the best_split tuple
    mask_left, mask_right, node_split_value, node_col = best_split[1:] 
    # print(f"{mask_left=}, {mask_right=}, {node_split_value=}, {node_col=}")

    # Give the current node the split_value and col it needs for predictions
    node.split_value_or_rows, node.col = node_split_value, node_col

    mask_left, mask_right = update_mask(x, mask_left, mask_right, current_mask)
    return [Node(split_value_or_rows=mask_left), Node(split_value_or_rows=mask_right)]

def update_mask(x, mask_left, mask_right, current_mask):
    """
    @todo: Docstring for update_mask
    """
    print(f"{current_mask=}")
    print(f"{mask_left=}")
    print(f"{mask_right=}")
    current_row_no = np.where(current_mask)
    print(f"{current_rows=}")
    return mask_left, mask_right
    

#
#
# Put all helper functions above this comment!


def tree_grow(x=None,
              y=None,
              n_min=None,
              min_leaf=None,
              n_feat=None,
              **defaults) -> Tree:
    """
    @todo: Docstring for tree_grow
    """
    # De nodelist heeft in het begin alleen een root node met alle rows van x,
    # omdat alle rows in de root in acht worden genomen voor bestsplit berekening.
    #
    # Dit representeren we met een boolean mask over x, met lengte het aantal rows
    # in x en elementen True. Deze boolean mask zullen we repeatedly gebruiken als een
    # mask over x om de rows voor bestsplit op te halen.
    mask = np.full(len(x), True)

    # Het eerste node object moet nu geinstantieerd worden
    root = Node(split_value_or_rows=mask)

    # We instantieren ook gelijk het Tree object
    tr = Tree(root)

    # De eerste nodelist heeft alleen de root node, daarna zijn twee childs,
    # etc. totdat alle splits gemaakt zijn en de lijst leeg is.
    nodelist = [root]

    while None not in nodelist:
        print(nodelist)
        # Pop de current node uit de nodelist
        node = nodelist.pop()
        print(nodelist)
        # Gebruik de boolean mask van de node om de rows in de node uit x te halen
        node_rows = x[node.split_value_or_rows]
        # Gebruik de boolean mask van de node om de classes in de node uit y te halen
        node_classes = y[node.split_value_or_rows]

        # print(f"{node_classes=}, {node_rows=}")

        # Test of de node een leaf node is met n_min
        if len(node_rows) < n_min:
            node.is_leaf_node(node_classes)
            continue

        # Als de node niet puur is, probeer dan te splitten
        if impurity(node_classes) > 0:
            # We gaan exhaustively voor de rows in de node over de cols
            # (age,married,house,income,gender) om de bestsplit te
            # bepalen
            #
            # We geven min_leaf als argument omdat:
            # "If the algorithm performs a split, it should be the best split that meets the minleaf constrain"
            #
            # We krijgen een exhaustive lijst terug met splits
            exhaustive_best_list = exhaustive_split_search(node_rows, node_classes, min_leaf)
            # print(exhaustive_best_list)
            # Als de lijst leeg is zijn er geen potentieele splits die voldoen
            # an de min leaf constraint
            if not exhaustive_best_list:
                node.is_leaf_node(node_classes)
                continue
            # Hier halen we de beste split, en rows voor de child/split nodes
            # uit de exhaustive best list
            best_split = max(exhaustive_best_list, key=lambda z: z[0])
            # Hier voegen we de twee nieuwe nodes toe aan de gesplitte "parent"
            nodelist += add_children(node, x, best_split)
            # node.add_split(left_child_node, right_child_node)
        else:
            node.is_leaf_node(node_classes)
            continue
    return tr

    # Initiate the nodelist with tuples of slice and class labels
    # nodelist = [Node(value=slices)]
    # tree = Tree(nodelist[0])
    # while nodelist:
    #     current_node = nodelist.pop()
    #     slices = current_node.value
    #     node_classes = y[slices]
    #     # print(node_classes)

    #     # f'Current node will be leaf node if (( (number of data "tuples" in child node) < {n_min=} )) \n'
    #     # put stopping rules here before making a split
    #     if len(node_classes) < n_min:
    #         current_node.value = Leaf(
    #             np.argmax(np.bincount(node_classes.astype(int))))
    #         print(f"leaf node has majority clas:\n{current_node.value.value=}")
    #         continue

    #     if impurity(node_classes) > 0:
    #         # print(
    #         #     f"Exhaustive split search says, new node will check these rows for potential spliterinos:\n{x[slices]}"
    #         # )

    #         # If we arrive here ever we are splitting
    #         # bestsplit(col, node_labels) ->
    #         # {"slices": list[int], "split": numpyfloat, "best_delta_i": numpyfloat}

    #         # slices (list) used for knowing which rows (int) to consider in a node
    #         # best_split saved in current_node.value
    #         # best_delta_i used to find best split among x_columns
    #         best_dict = None
    #         for i, x_col in enumerate(x[slices].transpose()):
    #             print(
    #                 "\nExhaustive split search says; \"Entering new column\":")
    #             col_split_dict = bestsplit(x_col, node_classes, slices)

    #             if best_dict is not None:
    #                 if col_split_dict["delta_i"] > best_dict["delta_i"]:
    #                     best_dict = col_split_dict
    #                     best_dict["col"] = i
    #             else:
    #                 best_dict = col_split_dict
    #                 best_dict["col"] = i
    #         print("\nThe best split for current node:", best_dict)

    #         # Here we store the splitted data into Node objects
    #         current_node.value = best_dict["split"]
    #         current_node.col = best_dict["col"]
    #         # Split will not happen if (( (number of data "tuples" potential split) < {min_leaf=} ))\n'
    #         if min([len(x) for x in best_dict["slices"].values()]) < min_leaf:
    #             continue
    #         else:
    #             # Invert left and right because we want left to pop() first
    #             children = [
    #                 Node(value=best_dict["slices"]["right"]),
    #                 Node(value=best_dict["slices"]["left"])
    #             ]
    #             current_node.add_split(children[1], children[0])
    #             nodelist += children
    #     else:
    #         current_node.value = Leaf(
    #             np.argmax(np.bincount(node_classes.astype(int))))
    #         print(
    #             f"\n\nLEAF NODE has majority clas:\n{current_node.value.value=}"
    #         )
    #         continue


def predict(x, nodes) -> list:
    """
    @todo: Docstring for predict
    """
    # which row to drop
    # print(x)
    drop = 0
    while not set(nodes).issubset({0, 1}):
        print(nodes)
        # print(x[drop])
        if isinstance(nodes[drop].value, Leaf):
            nodes[drop] = nodes[drop].value.value
            drop += 1
            continue

        print(nodes[drop].value)
        print(nodes[drop].col)
        # print(nodes[drop].col)
        if x[drop, nodes[drop].col] > nodes[drop].value:
            nodes[drop] = nodes[drop].left
        else:
            nodes[drop] = nodes[drop].right
    return np.array(nodes)


def tree_pred(x=None, tr=None, **defaults) -> np.array:
    """
    @todo: Docstring for tree_pred
    """
    nodes = [tr.tree] * len(x)
    # y = np.linspace(0, len(x), 0)
    # y = np.array(ele)
    y = predict(x, nodes)
    print(f"\n\nPredicted classes for {x=}\n\n are: {y=}")
    return y


if __name__ == '__main__':
    #### IMPURITY TEST
    # array=np.array([1,0,1,1,1,0,0,1,1,0,1])
    # print(impurity(array))
    # Should give 0.23....

    #### BESTSPLIT TEST
    # print(bestsplit(credit_data[:, 3], credit_data[:, 5]))
    # Should give 36

    #### TREE_GROW TEST
    tree_grow_defaults = {
        'x': credit_data[:, :5],
        'y': credit_data[:, 5],
        'n_min': 2,
        'min_leaf': 1,
        'n_feat': 5
    }

    # Calling the tree grow, unpacking default as argument
    tree_grow(**tree_grow_defaults)

    #### TREE_PRED TEST
    # tree_pred_defaults = {
    #     'x': credit_data[:, :5],
    #     'tr': tree_grow(**tree_grow_defaults)
    # }

    # tree_pred(**tree_pred_defaults)

# start_time = time.time()
# print("--- %s seconds ---" % (time.time() - start_time))
