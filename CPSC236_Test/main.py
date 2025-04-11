import time
import random
import csv
import threading
import os
from time import sleep

FILENAME = "CPSC_236_TestBank.csv"

def studentInfo():
    """
    Gets the Students First and Last name. Also get the 5 digits after The 'A' in their student ID
    Uses loopCount to track how many times an incorrect id was entered and exits the program if there are 3 consecutive incorrect inputs
    """
    loopCount = 0
    firstName = input("Enter first name:")
    lastName = input("Enter Last name:")
    while True:
        studentID = input("Enter 5 numbers after the 'A' in your ID:")
        if studentID.isnumeric() and len(studentID) == 5:
            break
        else:
            loopCount += 1
            if loopCount == 3:
                print("To many failed attempts. Exiting program.")
                exit()
            print("Make sure your ID is only 5 numbers long and not including the 'A' at the beginning")
    return firstName, lastName, 'A' + studentID

def getAllQuestions():
    """
    puts all the lines in a CSV into a list to get the total lines in the file

    :return: a list of all the questions in the file
    """
    allQuestionsInFile = []
    with open(FILENAME, newline="") as file:
        reader = csv.reader(file)
        for row in reader:
            allQuestionsInFile.append(row)
    return allQuestionsInFile

def getQuestions(totalQuestions):
    """
    Selects 10 or 20 questions, based on the user, at random and puts them in a list of lists.
    """
    questionNumbers = []
    questions = []
    allQuestions = getAllQuestions()

    while len(questionNumbers) != totalQuestions:
        randomNum = random.randint(2, len(allQuestions) - 1)
        if randomNum not in questionNumbers:
            questionNumbers.append(randomNum)

    for q in questionNumbers:
        questions.append(allQuestions[q])

    return questions

def threeAnswers(question):
    """
    This function prints questions and gets answer for questions with three answers
    """
    string_count = 64  # So that when it gets to the next string it will bge at 65 and can be turned into 'A' based on the ascii table
    for string in question:
        if string_count == 64:
            print("\n" +  string)
        elif string_count < 68:
            print(chr(string_count) + ". " + string)
        string_count += 1
    while True:
        answer = input("What is your answer (A, B, or C)").upper()
        if answer == 'A' or answer == 'B' or answer == 'C':
            break
        else:
            print("Error: Incorrect input. Make sure you typed in A, B, or C")
    return answer

def twoAnswers(question):
    """
    This function prints questions and gets answer for questions with two answers
    """
    string_count = 64  # So that when it gets to the next string it will bge at 65 and can be turned into 'A' based on the ascii table
    for string in question:
        if string_count == 64:
            print("\n" + string)
        elif string_count < 67:
            print(chr(string_count) + ". " + string)
        string_count += 1
    while True:
        answer = input("What is your answer (A or B)").upper()
        if answer == 'A' or answer == 'B':
            break
        else:
            print("Error: Incorrect input. Make sure you typed in A or B")
    return answer

def getScore(questions, answers):
    """
    This function takes in all the questions and all the answers. Then compares the answers to the correct answers.
    Then calculates the score based on in there were 10 or 20 questions.
    10 questions means each question is worth 1 point
    20 questions means each question is worth 0.5 points
    """
    totalQuestions = len(questions)
    question_count = 0
    correct = 0
    score = 0
    for question in questions:
        if question[4] == answers[question_count]:
            correct += 1
        question_count += 1
    if totalQuestions == 10:
        score = correct
    else:
        score = correct * 0.5
    return score

def createFile(firstName, lastName, studentID, questions, answers, score, elapsedTime):
    """
    This function writes StudentID, First name and Last name
    Score
    Elapsed time
    Selected questions text, and for each of the question the correct answer and the student’s answer
    """
    question_count = 0
    fileName = firstName + "_" + lastName + "_" + studentID + ".txt"
    with open(fileName, "w") as file:
        file.writelines(studentID + "\n")
        file.writelines(firstName + "\n")
        file.writelines(lastName + "\n")
        file.writelines("Your score is: " + str(score) + "\n")
        file.writelines("Your elapsedTime is " + str(round(elapsedTime)) + " seconds" + "\n")
        for question in questions:
            if answers[question_count] == 'A':
                answer = question[1]
            elif answers[question_count] == 'B':
                answer = question[2]
            elif answers[question_count] == 'C':
                answer = question[3]
            if question[4] == 'A':
                correctAnswer = question[1]
            elif question[4] == 'B':
                correctAnswer = question[2]
            elif question[4] == 'C':
                correctAnswer = question[3]
            file.writelines(str(question_count + 1) + ". " + question[0] + "\n")
            file.writelines("Correct answer is: " + correctAnswer + "\n")
            file.writelines("Your answer was: " + answer + "\n")
            question_count += 1
    print("\nYour file was created.")

def tenMinTimer(startTime, event):
    """
    This function is started on a different thread so that while the user is sitting at a question at an input
    it is still checking to see when the elapsed time reaches 10 min.
    Once it does it will print "Your time is up. Shutting down program" and shutdown the quiz.
    """

    print("\n10 min timer starts")
    elapsedTime = time.time() - startTime
    while not event.is_set():
        time.sleep(1)
        elapsedTime = time.time() - startTime
        if elapsedTime >= 600:
            print("\n\nYour time is up. Shutting down program")
            os._exit(0)

def main():
    firstName, lastName, studentID = studentInfo()

    while True:
        totalQuestions = int(input("Enter 10 or 20 for the number of Questions you would like to do:"))
        if totalQuestions == 10 or totalQuestions == 20:
            break
        else:
            print("Incorrect input. Try Again")

    questions = getQuestions(totalQuestions)
    answers = []
    score = 0
    startTime = time.time()
    stop_event = threading.Event()
    thread = threading.Thread(target=tenMinTimer, args=(startTime, stop_event,))
    thread.start()
    time.sleep(1)

    for question in questions:
        if question[3] == "":
            answer = twoAnswers(question)
        else:
            answer = threeAnswers(question)
        answers.append(answer)

    score = getScore(questions, answers)

    endTime = time.time()
    elapsedTime = endTime - startTime

    createFile(firstName, lastName, studentID, questions, answers, score, elapsedTime)

    stop_event.set()
    thread.join()

if __name__ == "__main__":
    running = True
    while running:
        os.system('cls' if os.name == 'nt' else 'clear')
        main()
        while True:
            x = input("Start the program again? (Q to exit and S to Start again)")
            if x.upper() == 'Q':
                print("Bye!")
                running = False
                break
            elif x.upper() != 'S':
                print("Incorrect input. Try again")
            else:
                break