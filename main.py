import datetime
import json
from os import getcwd
from os import listdir
from os.path import exists
#import atexit
from tkinter import *


class EmployeeNotFound(Exception):
    
    def __init__(self, f_name, s_name):
        self.f_name = f_name
        self.s_name = s_name
        self.message = f"The employee ({f_name} {s_name}) has not registered yet!"
        super().__init__(self.message)

    def __str__(self):
        return f"The employee ({self.f_name} {self.s_name}) has not registered yet!"


class WrongDateType(Exception):
    
    def __init__(self):
        self.message = "Доступні наступні формати дати: \nдд/мм/рррр \nдд-мм-рррр \nдд.мм.рррр"  
        super().__init__(self.message)

    def __str__(self):
        return "Доступні наступні формати дати: \nдд/мм/рррр \nдд-мм-рррр \nдд.мм.рррр"  



class Employee:
    
    def __init__(self, f_name: str, s_name: str, date = None):
        self.f_name = f_name
        self.s_name = s_name

        if all((date, f_name, s_name)):
            self.f_name = f_name
            self.s_name = s_name
            self.date = self._parse_date(date)
            self._vacation_days = [self.date, 0]
            self.breaks = list()
        else:
            if exists(f"{getcwd()}/people/{self.f_name}_{self.s_name}.json"):
                with open(f"{getcwd()}/people/{self.f_name}_{self.s_name}.json", 'r') as jfile:
                    json_obj = json.load(jfile)
                    self.f_name = json_obj["first_name"]
                    self.s_name = json_obj["second_name"]
                    self.date = datetime.datetime.fromtimestamp(json_obj["start"])
                    self._vacation_days = [datetime.datetime.fromtimestamp(json_obj["vacation"][0]), json_obj["vacation"][1]]
                    self.breaks = json_obj["breaks"]
            else:
                raise EmployeeNotFound(self.f_name, self.s_name)
        self.__calc_vacation_days()
        #atexit.register(self._save)
 
    
    def _parse_date(self, string) -> datetime.datetime:
        if '/' in string:
            day, month, year = string.split('/')
        elif '-' in string:   
            day, month, year = string.split('-')
        elif '.' in string:
            day, month, year = string.split('.')
        else:
            raise WrongDateType
        
        date = tuple(map(int, (year, month, day)))
    
        return datetime.datetime(*date)
        
    
    def _save(self):
        dictionary = {
                "first_name": self.f_name,
                "second_name": self.s_name,
                "start": self.date.timestamp(),
                "vacation": [self._vacation_days[0].timestamp(), self._vacation_days[1]],
                "breaks": self.breaks
                }
        json_obj = json.dumps(dictionary, indent=4)
        with open(f"{getcwd()}/people/{self.f_name}_{self.s_name}.json", 'w') as jfile:
            jfile.write(json_obj)
        print("Saved!" + self.s_name + self.f_name )


    def take_payed_vacation(self, start: str, finish: str):
        start = self._parse_date(start)
        finish = self._parse_date(finish)
        delta_days = finish - start
        self._vacation_days[1] -= delta_days.days
        self._vacation_days[0] = datetime.datetime.today()
        print(self._vacation_days)
        
        
    def add_break(self, start: datetime.datetime, finish: datetime.datetime, reason: str):
        delta_days = finish - start
        self.breaks.append((start.timestamp(), finish.timestamp(), reason, delta_days.days))
        self.__calc_vacation_days()
    

    def _sum_breaks(self, start: datetime.datetime):
        suma = 0
        for break_ in self.breaks:
            break_start = datetime.datetime.fromtimestamp(break_[0])
            break_stop = datetime.datetime.fromtimestamp(break_[1])
            if break_stop > start:
                if break_start >= start:
                    suma += break_[3]
                else:
                    s = break_stop-start
                    suma += s.days
        return suma
                

    def __calc_vacation_days(self):

        today = datetime.datetime.today()
        total_days = today - self._vacation_days[0]
        total_breaks = self._sum_breaks(self._vacation_days[0])
        self._vacation_days = [today, self._vacation_days[1]+(total_days.days - total_breaks)/365*24]
    

    def __del__(self):
        try:
            self._save()
        except NameError:
            pass

    
    def __str__(self):
        return f"""Employee: {self.f_name} {self.s_name}\nHired: {self.date.strftime('%x')}\nVacation: {self._vacation_days[1]} """



class App:
    def __init__(self, root: Tk):
        self.selected = None
        self.workers = None
        
        self.main = root
        self.main.geometry("600x350")
        self.main.title("Відпустки")
        self._widgets()
        
        
    def _widgets(self):

        self.workersLstBox = Listbox(self.main, height=10, font=("arial", 16))
        self.workersLstBox.grid(column=0, row=0, rowspan=10)
        self.workersLstBox.bind('<Double-Button-1>', self._view)

        self._update()

        self.infoLbl = Label(self.main, font=("arial", 14), fg='blue')
        self.infoLbl.grid(column=1, row=0, rowspan=4, columnspan=2)
        
        self.updateBtn = Button(self.main,
                             text="Update", 
                             font=("arial", 14),
                             command=self._update)
        self.updateBtn.grid(column=0, row=10)
        
        self.addBtn = Button(self.main,
                             text="Додати працівника", 
                             font=("arial", 17),
                             command=self._add_employee)
        self.addBtn.grid(column=1, row=4, rowspan=2, columnspan=2)

        self.vacBtn = Button(self.main,
                             text="Надати оплачувану відпустку", 
                             font=("arial", 17),
                             command=self._add_vacation)
        self.vacBtn.grid(column=1, row=6, rowspan=2, columnspan=2)

        self.breakBtn = Button(self.main,
                             text="Додати неробочі дні", 
                             font=("arial", 17),
                             command=self._add_break)
        self.breakBtn.grid(column=1, row=8, rowspan=2, columnspan=2)
    
    
    def _parse_date(self, string) -> datetime.datetime:
        pass

    
    def _update(self):
        self.workers = sorted([(worker[:-5].split('_')[0], worker[:-5].split('_')[1]) for worker in listdir(f"{getcwd()}/people/")])
        self.workersLstBox.delete(0, END)
        
        for worker in self.workers:
            self.workersLstBox.insert(END, ' '.join(worker))

    
    def _view(self, event):
        self.selected = Employee(*self.workers[self.workersLstBox.curselection()[0]])
        txt = str(self.selected)
        self.infoLbl.configure(text=txt)

    
    def _add_employee(self):
        root = Toplevel()
        root.title("Новий працівник")
        toplevelCreator(root, {0: "Ім'я", 1: "Прізвище", 2: "Дата працевлаштування"}, Employee)
        root.mainloop()
                

    def _add_vacation(self):
        if self.selected is None:
            self.infoLbl.configure(text="Спочатку оберіть \nпрацівника!")
        else:
            root = Toplevel()
            root.title("Відпустка")
            toplevelCreator(root, {0: "Дата початку відпустки", 1: "Дата кінця відпустки"}, self.selected.take_payed_vacation)
            del self.selected
            root.mainloop()
        

    def _add_break(self):
        pass


            
def toplevelCreator(root, questions: dict, func):
    
    entries = []
    labels = []
    results = [StringVar() for i in questions]
    r = 0
    for key, value in questions.items():
       lbl = Label(root, text=value, font=("arial", 16))
       lbl.grid(column=0, row=r)
       labels.append(lbl)
       
       entry = Entry(root, textvariable=results[key], font=("arial", 16))
       entry.grid(column=1, row=r)
       entries.append(entry)
       
       r += 1

    info = Label(root, text='', font=("arial", 16), fg='red')
    info.grid(column=0, columnspan=2, row=r)
 
    def click():
        nonlocal results, root, info
        try:
            a = func(*list(var.get().strip() for var in results))
            del a
            root.destroy()
        except Exception as err:
            info.configure(text=err)
            

    btn = Button(root, text="Підтвердити", font=("arial", 16), command=click)
    btn.grid(row=r+1, column=0, columnspan=2)
          
    
 
if __name__ == "__main__":
    root = Tk()
    app = App(root)
    root.mainloop() 