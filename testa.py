


if __name__ == '__main__':
    with open('data_list.txt', 'r') as f:
        res = f.read()
        # print res
    res = res.replace(' ', '').replace('\n', '')
    res = res.split('7e7e')
    print res