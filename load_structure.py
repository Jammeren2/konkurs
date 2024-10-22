import os

def print_directory_contents(path, level=0):
    # Получаем список всех файлов и папок в указанной директории
    try:
        items = os.listdir(path)
    except PermissionError:
        return  # Игнорируем директории, к которым нет доступа
    
    # Сортируем элементы по имени, чтобы сначала были папки, потом файлы
    items.sort()
    
    # Проходим по каждому элементу
    for item in items:
        item_path = os.path.join(path, item)
        # Печатаем с отступами, соответствующими уровню вложенности
        print('   ' * level + '/' + item)
        
        # Если это папка, рекурсивно обрабатываем её содержимое
        if os.path.isdir(item_path):
            print_directory_contents(item_path, level + 1)

# Указываем путь к корневой папке
folder_path = 'C:/Users/my/Documents/GitHub/konkurs'
print_directory_contents(folder_path)
