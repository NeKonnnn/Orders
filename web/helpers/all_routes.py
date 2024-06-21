import os


def find_route_function_pairs(directory):
    """
    Crawls through the given directory and its subdirectories to find files containing
    '@app<.>route' and their subsequent function definitions. Ignores folders starting with '.'.
    """
    for root, dirs, files in os.walk(directory):
        # Skip hidden directories (those starting with '.')
        dirs[:] = [d for d in dirs if not d.startswith('.')]
        # files[:] = [f for f in files if not f.endswith('html')]
        for file in files:
            file_path = os.path.join(root, file)
            try:
                print(file_path.replace('../', ''))
                with open(file_path, 'r', encoding='utf-8') as f:
                    pass
                    # lines = f.readlines()
                    # print(lines)

                # for i in range(len(lines) - 1):
                #     if '@app.route' in lines[i]:
                #         print("===")
                #         print(file_path)
                #         print(lines[i].strip())
                #         print(lines[i + 1].strip())

            except Exception:
                pass


# Example usage
find_route_function_pairs('../')

