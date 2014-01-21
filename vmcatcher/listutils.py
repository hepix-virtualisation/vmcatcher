
def pairsNnot(list_a,list_b):
    len_generate_list = len(list_a)
    len_image_list = len(list_b)
    ocupies_generate_list = set(range(len_generate_list))
    ocupies_image_list = set(range(len_image_list))
    ocupies_pairs = ocupies_image_list.intersection(ocupies_generate_list)
    diff_a = ocupies_generate_list.difference(ocupies_image_list)
    diff_b = ocupies_image_list.difference(ocupies_generate_list)
    arepairs = []
    for i in ocupies_pairs:
        arepairs.append([list_a[i],list_b[i]])
    notpairs_a = []
    for i in diff_a:
        notpairs_a.append(list_a[i])
    notpairs_b = []
    for i in diff_b:
        notpairs_b.append(list_b[i])

    return arepairs,notpairs_a,notpairs_b
