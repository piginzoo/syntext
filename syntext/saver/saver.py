class Saver:

    def parse_lines(self, image_path, label):
        raise NotImplementedError("子类实现")

    def get_label_name(self, image_path):
        raise NotImplementedError("子类实现")

    def save(self, image_path, label):
        lines = self.parse_lines(image_path, label)
        label_file_name = self.get_label_name(image_path)

        label_file = open(label_file_name, 'w', encoding='utf-8')
        for line in lines:
            label_file.write(line)
            label_file.write("\n")
        label_file.close()
