import os

class FileManager:
    def __init__(self, folder="data/arquivos"):
        self.folder = folder
        if not os.path.exists(self.folder):
            os.makedirs(self.folder)
        print(f"Gerenciador de arquivos inicializado na pasta: {self.folder}")

    def _validate_filename(self, filename):
        if not filename or '..' in filename or '/' in filename or '\\' in filename:
            return False
        return True

    def list_files(self):
        try:
            return os.listdir(self.folder)
        except Exception as e:
            print(f"Erro ao listar arquivos: {str(e)}")
            return []

    def create_file(self, filename, content=""):
        if not self._validate_filename(filename):
            return False, "Nome de arquivo inválido ou inseguro."

        filepath = os.path.join(self.folder, filename)
        if os.path.exists(filepath):
            return False, f"O arquivo '{filename}' já existe. Use a função edit_file para modificá-lo."

        try:
            with open(filepath, "w", encoding="utf-8") as f:
                f.write(content)
            print(f"Arquivo criado: {filename}")
            return True, f"Arquivo '{filename}' criado com sucesso."
        except Exception as e:
            print(f"Erro ao criar arquivo {filename}: {str(e)}")
            return False, str(e)

    def read_file(self, filename):
        if not self._validate_filename(filename):
            return False, "Nome de arquivo inválido ou inseguro."

        filepath = os.path.join(self.folder, filename)
        if not os.path.exists(filepath):
            return False, "Arquivo não encontrado."

        try:
            with open(filepath, "r", encoding="utf-8") as f:
                content = f.read()
            print(f"Arquivo lido: {filename}")
            return True, content
        except Exception as e:
            print(f"Erro ao ler arquivo {filename}: {str(e)}")
            return False, str(e)

    def edit_file(self, filename, content):
        if not self._validate_filename(filename):
            return False, "Nome de arquivo inválido ou inseguro."

        filepath = os.path.join(self.folder, filename)
        if not os.path.exists(filepath):
            return False, "Arquivo não encontrado."

        try:
            with open(filepath, "w", encoding="utf-8") as f:
                f.write(content)
            print(f"Arquivo editado: {filename}")
            return True, f"Arquivo '{filename}' editado com sucesso."
        except Exception as e:
            print(f"Erro ao editar arquivo {filename}: {str(e)}")
            return False, str(e)

    def remove_file(self, filename):
        if not self._validate_filename(filename):
            return False, "Nome de arquivo inválido ou inseguro."

        filepath = os.path.join(self.folder, filename)
        if not os.path.exists(filepath):
            return False, "Arquivo não encontrado."

        try:
            os.remove(filepath)
            print(f"Arquivo removido: {filename}")
            return True, f"Arquivo '{filename}' removido com sucesso."
        except Exception as e:
            print(f"Erro ao remover arquivo {filename}: {str(e)}")
            return False, str(e)
