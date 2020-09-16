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


class Node():
    """
    @todo: docstring for Node
    """
    def __init__(self, value=None):
        """@todo: Docstring for init method.

        /value=None/ @todo

        """
        self.value = value

    def add_split(self, left, right):
        """
        @todo: Docstring for add_split
        """
        self.left = left
        self.right = right


class Leaf:
    def __init__(self, predicted_class: int):
        self.predicted_class = predicted_class


class Tree():
    """
    @todo: docstring for Tree
    """
    def __init__(self, root_node_obj):
        """@todo: Docstring for init method.

        /root_node_obj/ @todo

        """
        self.tree = root_node_obj

    def __repr__(self):
        nodelist = [self.tree]
        tree_str = ''
        while nodelist:
            current_node = nodelist.pop()
            # print(current_node.value)
            try:
                childs = [current_node.right, current_node.left]
                nodelist += childs
            except AttributeError:
                pass
            col, c = current_node.value
            tree_str += f"{col=}, {c=}"
        return tree_str


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


def bestsplit(x, y) -> int:
    """
    x = vector of num values
    y = vector of class labels ... array([{x: x is 0 or 1}]) ??

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
        # Turns binary attributes from [0,1] to [0, 0.5], allows us to use
        # normal slices
        split_points = x_sorted / 2
    else:
        split_points = (x_sorted[:len(x_sorted) - 1] + x_sorted[1:]) / 2

    best_dict = None
    for split in split_points:
        # Returns boolean matrix which can be used for slicing x
        x_slices = {
            "left": np.index_exp[x > split],
            "right": np.index_exp[x <= split]
        }

        # delta_i formule
        delta_i = impurity(y) - (len(y[x_slices["left"]]) * impurity(
            y[x_slices["left"]]) + len(y[x_slices["right"]]) *
                                 impurity(y[x_slices["right"]])) / len(y)

        print(f"{split=}, {delta_i=}")
        if best_dict is not None:
            if delta_i > best_dict["delta_i"]:
                best_dict = {"x_slices": x_slices, "split": split, "delta_i":delta_i}
        else:
            best_dict = {"slices": x_slices, "split": split, "delta_i":delta_i}
    return best_dict

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
    all_rows = np.index_exp[:]
    # Initiate the nodelist with tuples of slice and class labels
    nodelist = [Node(value={"slices": all_rows})]
    tree = Tree(nodelist[0])
    while nodelist:
        current_node = nodelist.pop()
        slices = current_node.value["slices"]
        print(f"Exhaustive split search says, new node will check these rows for potential spliterinos:\n{x[slices]}")

        if impurity(y[slices]) > 0:

            # bestsplit(col, node_labels) -> 
            # {"x_slices": (boolean matrix, boolean matrix), "split": numpyfloat, "best_delta_i": numpyfloat}

            # slices used for knowing where to split on the next node.
            # best_split saved in current_node.value
            # best_delta_i used to find best split among x_columns
            best_dict = None
            for x_col in x[slices].transpose():
                print("\nExhaustive split search says; \"Entering new column\":")
                col_split_dict = bestsplit(x_col, y[slices])

                if best_dict is not None:
                    if col_split_dict["delta_i"] > best_dict["delta_i"]:
                        best_dict = col_split_dict
                else:
                    best_dict = col_split_dict
            print("\nThe best split for current node:", best_dict)

    return tree



def tree_pred(x=None, tr=None, **defaults) -> np.array:
    """
    @todo: Docstring for tree_pred
    """
    y = np.array([])
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

    # tree_pred_defaults = {
    #     'x': credit_data[:, :5],
    #     'tr': tree_grow(**tree_grow_defaults)
    # }

    # tree_pred(**tree_pred_defaults)

