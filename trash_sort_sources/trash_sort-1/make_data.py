import yaml
import glob

train_list = glob.glob('./train/images/*.jpg')
valid_list = glob.glob('./valid/images/*.jpg')
test_list = glob.glob('./test/images/*.jpg')

with open('/home/skh/semi_projects/trash_sort/src/trash_sort_sources/trash_sort-1/train.txt', 'w') as f:
    f.write('\n'.join(train_list) + '\n')

with open('/home/skh/semi_projects/trash_sort/src/trash_sort_sources/trash_sort-1/valid.txt', 'w') as f:
    f.write('\n'.join(valid_list) + '\n')
    
with open('/home/skh/semi_projects/trash_sort/src/trash_sort_sources/trash_sort-1/test.txt', 'w') as f:
    f.write('\n'.join(test_list) + '\n')


# /home/skh/semi_projects/trash_sort/src/trash_sort_sources/trash_sort-1

with open('/home/skh/semi_projects/trash_sort/src/trash_sort_sources/trash_sort-1/data.yaml', 'r') as f:
  data = yaml.load(f)

print(data)
data['train'] = '/home/skh/semi_projects/trash_sort/src/trash_sort_sources/trash_sort-1/train.txt'
data['val'] = '/home/skh/semi_projects/trash_sort/src/trash_sort_sources/trash_sort-1/valid.txt'
data['test'] = '/home/skh/semi_projects/trash_sort/src/trash_sort_sources/trash_sort-1/test.txt'

# dump means, python 객체를 yaml형태의 문자열로 반환하는 의미.
with open('/home/skh/semi_projects/trash_sort/src/trash_sort_sources/trash_sort-1/data.yaml', 'w') as f:
  yaml.dump(data, f)

# print(data)