def indexing(array):
    i = 5
    while (i != 0):
        i -= 1
        int_ind_arr = int(array[i])
        if int_ind_arr == 9:
            array[i] = "0"
        else:
            int_ind_arr += 1
            array[i] = str(int_ind_arr)
            break
    return array