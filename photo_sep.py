import os
import sys
import shutil


if __name__ == '__main__':
    base_path = os.path.dirname(os.path.abspath(__file__))
    dorm_file = sys.argv[1]
    
    copied = {
        'error': 0,
        'success': 0,
        'skipped' : 0,
    }
    for line in open(os.path.join(base_path, 'data', dorm_file)):
        line = line.strip()
        if not line or line.startswith('#'):
            continue
        room, stds = line.split('=')
        room_dir = os.path.join(base_path, 'report', 'photos', room.replace('/', '-'))
        if not os.path.exists(room_dir):
            os.makedirs(room_dir)
        for std in stds.split(','):
            pic_addr = os.path.join(room_dir, std + '.jpg')
            if not os.path.exists(pic_addr):
                try:
                    shutil.copy2(os.path.join(base_path, 'data', 'photos', std[:2], std + '.jpg'), pic_addr)
                except Exception as e:
                    copied['error'] += 1
                    raise e
                else:
                    copied['success'] += 1
            else:
                copied['skipped'] += 1

    print 'Pictures copied!'
    print copied

