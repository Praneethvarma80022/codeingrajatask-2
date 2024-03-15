from tkinter import *
from tkinter import ttk as ttk
from tkinter import messagebox as mb
import datetime
import sqlite3
from tkcalendar import DateEntry

def listAllExpenses():
    global dbconnector, data_table
    data_table.delete(*data_table.get_children())
    all_data = dbconnector.execute('SELECT * FROM ExpenseTracker')
    data = all_data.fetchall()
    for val in data:
        data_table.insert('', END, values=val)

def viewExpenseInfo():
    global data_table
    global dateField, payee, description, amount, modeOfPayment
    if not data_table.selection():
        mb.showerror('No expense selected', 'Please select an expense from the table to view its details')
    currentSelectedExpense = data_table.item(data_table.focus())
    val = currentSelectedExpense['values']
    expenditureDate = datetime.date(int(val[1][:4]), int(val[1][5:7]), int(val[1][8:]))
    dateField.set_date(expenditureDate)
    payee.set(val[2])
    description.set(val[3])
    amount.set(val[4])
    modeOfPayment.set(val[5])

def clearFields():
    global description, payee, amount, modeOfPayment, dateField, data_table
    todayDate = datetime.datetime.now().date()
    description.set('')
    payee.set('')
    amount.set(0.0)
    modeOfPayment.set('Cash')
    dateField.set_date(todayDate)
    data_table.selection_remove(*data_table.selection())

def removeExpense():
    if not data_table.selection():
        mb.showerror('No record selected!', 'Please select a record to delete!')
        return
    currentSelectedExpense = data_table.item(data_table.focus())
    valuesSelected = currentSelectedExpense['values']
    confirmation = mb.askyesno('Are you sure?', f'Are you sure that you want to delete the record of {valuesSelected[2]}')
    if confirmation:
        dbconnector.execute('DELETE FROM ExpenseTracker WHERE ID=%d' % valuesSelected[0])
        dbconnector.commit()
        listAllExpenses()
        mb.showinfo('Record deleted successfully!', 'The record you wanted to delete has been deleted successfully')

def removeAllExpenses():
    confirmation = mb.askyesno('Are you sure?', 'Are you sure that you want to delete all the expense items from the database?', icon='warning')
    if confirmation:
        data_table.delete(*data_table.get_children())
        dbconnector.execute('DELETE FROM ExpenseTracker')
        dbconnector.commit()
        clearFields()
        listAllExpenses()
        mb.showinfo('All Expenses deleted', 'All the expenses were successfully deleted')
    else:
        mb.showinfo('Ok then', 'The task was aborted and no expense was deleted!')

def addAnotherExpense():
    global dateField, payee, description, amount, modeOfPayment, dbconnector
    if not dateField.get() or not payee.get() or not description.get() or not amount.get() or not modeOfPayment.get():
        mb.showerror('Fields empty!', "Please fill all the missing fields before pressing the add button!")
    else:
        dbconnector.execute(
            'INSERT INTO ExpenseTracker (Date, Payee, Description, Amount, ModeOfPayment) VALUES (?, ?, ?, ?, ?)',
            (dateField.get_date(), payee.get(), description.get(), amount.get(), modeOfPayment.get())
        )
        dbconnector.commit()
        clearFields()
        listAllExpenses()
        mb.showinfo('Expense added', 'The expense whose details you just entered has been added to the database')

def editExpense():
    global data_table
    def editExistingExpense():
        global dateField, amount, description, payee, modeOfPayment, dbconnector, data_table
        currentSelectedExpense = data_table.item(data_table.focus())
        content = currentSelectedExpense['values']
        dbconnector.execute(
            'UPDATE ExpenseTracker SET Date = ?, Payee = ?, Description = ?, Amount = ?, ModeOfPayment = ? WHERE ID = ?',
            (dateField.get_date(), payee.get(), description.get(), amount.get(), modeOfPayment.get(), content[0])
        )
        dbconnector.commit()
        clearFields()
        listAllExpenses()
        mb.showinfo('Data edited', 'We have updated the data and stored in the database as you wanted')
        editSelectedButton.destroy()
    if not data_table.selection():
        mb.showerror('No expense selected!', 'You have not selected any expense in the table for us to edit; please do that!')
        return
    viewExpenseInfo()
    editSelectedButton = Button(
        frameL3,
        text="Edit Expense",
        font=("Bahnschrift Condensed", "13"),
        width=30,
        bg="#90EE90",
        fg="#000000",
        relief=GROOVE,
        activebackground="#008000",
        activeforeground="#98FB98",
        command=editExistingExpense
    )
    editSelectedButton.grid(row=0, column=0, sticky=W, padx=50, pady=10)

def selectedExpenseToWords():
    global data_table
    if not data_table.selection():
        mb.showerror('No expense selected!', 'Please select an expense from the table for us to read')
        return
    currentSelectedExpense = data_table.item(data_table.focus())
    val = currentSelectedExpense['values']
    msg = f'Your expense can be read like: \n"You paid {val[4]} to {val[2]} for {val[3]} on {val[1]} via {val[5]}"'
    mb.showinfo('Here\'s how to read your expense', msg)

def expenseToWordsBeforeAdding():
    global dateField, description, amount, payee, modeOfPayment
    if not dateField.get() or not payee.get() or not description.get() or not amount.get() or not modeOfPayment.get():
        mb.showerror('Incomplete data', 'The data is incomplete, meaning fill all the fields first!')
    else:
        msg = f'Your expense can be read like: \n"You paid {amount.get()} to {payee.get()} for {description.get()} on {dateField.get_date()} via {modeOfPayment.get()}"'
    addQuestion = mb.askyesno('Read your record like: ', f'{msg}\n\nShould I add it to the database?')
    if addQuestion:
        addAnotherExpense()
    else:
        mb.showinfo('Ok', 'Please take your time to add this record')

if __name__ == "__main__":
    dbconnector = sqlite3.connect("Expense_Tracker.db")
    dbcursor = dbconnector.cursor()
    dbconnector.execute(
        'CREATE TABLE IF NOT EXISTS ExpenseTracker (ID INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL, Date DATETIME, Payee TEXT, Description TEXT, Amount FLOAT, ModeOfPayment TEXT)'
    )
    dbconnector.commit()

    main_win = Tk()
    main_win.title("PERSONAL BUDGET TRACKER")
    main_win.geometry("1415x650+400+100")
    main_win.resizable(0, 0)
    main_win.config(bg="#FFFAF0")

    frameLeft = Frame(main_win, bg="#FFF8DC")
    frameLeft.grid(row=0, column=0, padx=10, pady=5)

    frameRight = Frame(main_win, bg="#FFF8DC")
    frameRight.grid(row=0, column=1, padx=10, pady=5)

    frameBott = Frame(main_win, bg="#FFF8DC")
    frameBott.grid(row=1, column=0, padx=10, pady=5, columnspan=2)

    ttk.Label(frameLeft, text="PERSONAL BUDGET", font=("Bahnschrift Condensed", "23", "bold"), background="#FFF8DC").grid(
        row=0, column=0, padx=10, pady=10
    )

    data_table = ttk.Treeview(
        frameLeft,
        columns=("ID", "Date", "Payee", "Description", "Amount", "ModeOfPayment"),
        show='headings',
        height=19,
        selectmode="extended"
    )
    data_table.heading("ID", text="ID")
    data_table.heading("Date", text="Date")
    data_table.heading("Payee", text="Payee")
    data_table.heading("Description", text="Description")
    data_table.heading("Amount", text="Amount")
    data_table.heading("ModeOfPayment", text="ModeOfPayment")

    data_table.column("ID", minwidth=30, width=30)
    data_table.column("Date", minwidth=100, width=100)
    data_table.column("Payee", minwidth=100, width=100)
    data_table.column("Description", minwidth=100, width=100)
    data_table.column("Amount", minwidth=100, width=100)
    data_table.column("ModeOfPayment", minwidth=100, width=100)

    data_table.grid(row=1, column=0, padx=10, pady=10, sticky="NSEW")
    frameLeft.grid_rowconfigure(1, weight=1)
    frameLeft.grid_columnconfigure(0, weight=1)

    frameL3 = Frame(frameRight, bg="#FFF8DC")
    frameL3.grid(row=2, column=0, pady=10)

    dateField = DateEntry(
        frameL3,
        font=("Bahnschrift Condensed", "15"),
        width=18,
        background="#90EE90",
        foreground="#000000",
        borderwidth=2,
        date_pattern="yyyy-mm-dd"
    )
    dateField.grid(row=0, column=1, padx=5, pady=5)

    Label(frameL3, text="Date: ", font=("Bahnschrift Condensed", "15"), bg="#FFF8DC").grid(row=0, column=0, padx=5, pady=5)

    Label(frameL3, text="Payee: ", font=("Bahnschrift Condensed", "15"), bg="#FFF8DC").grid(row=1, column=0, padx=5, pady=5)
    payee = StringVar()
    payeeEntry = Entry(frameL3, font=("Bahnschrift Condensed", "15"), width=20, textvariable=payee)
    payeeEntry.grid(row=1, column=1, padx=5, pady=5)

    Label(frameL3, text="Description: ", font=("Bahnschrift Condensed", "15"), bg="#FFF8DC").grid(row=2, column=0, padx=5, pady=5)
    description = StringVar()
    descEntry = Entry(frameL3, font=("Bahnschrift Condensed", "15"), width=20, textvariable=description)
    descEntry.grid(row=2, column=1, padx=5, pady=5)

    Label(frameL3, text="Amount: ", font=("Bahnschrift Condensed", "15"), bg="#FFF8DC").grid(row=3, column=0, padx=5, pady=5)
    amount = DoubleVar()
    amountEntry = Entry(frameL3, font=("Bahnschrift Condensed", "15"), width=20, textvariable=amount)
    amountEntry.grid(row=3, column=1, padx=5, pady=5)

    Label(frameL3, text="Mode of Payment: ", font=("Bahnschrift Condensed", "15"), bg="#FFF8DC").grid(row=4, column=0, padx=5, pady=5)
    modeOfPayment = StringVar()
    modeOfPaymentEntry = Entry(frameL3, font=("Bahnschrift Condensed", "15"), width=20, textvariable=modeOfPayment)
    modeOfPaymentEntry.grid(row=4, column=1, padx=5, pady=5)

    Button(
        frameL3,
        text="Add New Expense",
        font=("Bahnschrift Condensed", "15"),
        width=30,
        bg="#90EE90",
        fg="#000000",
        relief=GROOVE,
        activebackground="#008000",
        activeforeground="#98FB98",
        command=expenseToWordsBeforeAdding
    ).grid(row=5, column=0, columnspan=2, padx=5, pady=5)

    Button(
        frameL3,
        text="Clear Fields",
        font=("Bahnschrift Condensed", "15"),
        width=30,
        bg="#90EE90",
        fg="#000000",
        relief=GROOVE,
        activebackground="#008000",
        activeforeground="#98FB98",
        command=clearFields
    ).grid(row=6, column=0, columnspan=2, padx=5, pady=5)

    Button(
        frameL3,
        text="Edit Selected Expense",
        font=("Bahnschrift Condensed", "15"),
        width=30,
        bg="#90EE90",
        fg="#000000",
        relief=GROOVE,
        activebackground="#008000",
        activeforeground="#98FB98",
        command=editExpense
    ).grid(row=7, column=0, columnspan=2, padx=5, pady=5)

    Button(
        frameL3,
        text="Remove Selected Expense",
        font=("Bahnschrift Condensed", "15"),
        width=30,
        bg="#90EE90",
        fg="#000000",
        relief=GROOVE,
        activebackground="#008000",
        activeforeground="#98FB98",
        command=removeExpense
    ).grid(row=8, column=0, columnspan=2, padx=5, pady=5)

    Button(
        frameL3,
        text="Remove All Expenses",
        font=("Bahnschrift Condensed", "15"),
        width=30,
        bg="#90EE90",
        fg="#000000",
        relief=GROOVE,
        activebackground="#008000",
        activeforeground="#98FB98",
        command=removeAllExpenses
    ).grid(row=9, column=0, columnspan=2, padx=5, pady=5)

    Button(
        frameL3,
        text="View Selected Expense",
        font=("Bahnschrift Condensed", "15"),
        width=30,
        bg="#90EE90",
        fg="#000000",
        relief=GROOVE,
        activebackground="#008000",
        activeforeground="#98FB98",
        command=viewExpenseInfo
    ).grid(row=10, column=0, columnspan=2, padx=5, pady=5)

    Button(
        frameL3,
        text="Read Selected Expense",
        font=("Bahnschrift Condensed", "15"),
        width=30,
        bg="#90EE90",
        fg="#000000",
        relief=GROOVE,
        activebackground="#008000",
        activeforeground="#98FB98",
        command=selectedExpenseToWords
    ).grid(row=11, column=0, columnspan=2, padx=5, pady=5)

    listAllExpenses()

    main_win.mainloop()
