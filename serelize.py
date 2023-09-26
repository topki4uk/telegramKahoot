import json


class Task:
    def __init__(self, question, options, correct_answer):
        self.question = question
        self.options = options
        self.correct_answer = correct_answer

    def __iter__(self):
        return iter(self.options)


class KHTFile:
    def __init__(self, file):
        self.file = json.loads(file)
        self.tasks = []

        self.title = self.file['title']

        for task in self.file['questions']:
            question = task['question']
            options = task['options']
            answer = task['answer']

            task_dict = Task(question, options, answer)
            self.tasks.append(task_dict)

    def __setattr__(self, key, value):
        self.__dict__[key] = value

    def __iter__(self):
        return iter(self.tasks)

    def __len__(self):
        return len(self.tasks)


def main():
    with open(r'quiz.json', 'r', encoding='utf8') as file:
        kht = KHTFile(file.read())
        print(kht.title)

        for n, task in enumerate(kht):
            print(f'{n+1}. {task.question}')
            for i, answer in enumerate(task.options):
                print(f'{i+1}. {answer}')
            print(f'Правильный ответ: {task.correct_answer}')


if __name__ == '__main__':
    main()
