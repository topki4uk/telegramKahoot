class KHTFile:
    def __init__(self, file):
        self.file = file
        self.tasks = {
            'questions': []
        }

        title, *tasks = file.split('-'*20)
        self.tasks['title'] = title[title.index(':')+1:].strip()

        for task in tasks:
            question, *answers = task.strip().split('\n')
            question = question[question.index(':')+1:].strip()
            question_dict = {
                'question': question,
                'answers': {}
            }

            for answer in answers:
                q = answer[answer.index(':')+1:answer.index('->')-1].strip()
                a = True if answer[answer.index('->')+2:].strip() == 'T' else False
                question_dict['answers'][q] = a

            self.tasks['questions'].append(question_dict)

    def __getitem__(self, item):
        return self.tasks[item]


def main():
    with open(r'kht_files/quiz.kht', 'r') as file:
        kht = KHTFile(file.read())
        print(kht['questions'])


if __name__ == '__main__':
    main()
