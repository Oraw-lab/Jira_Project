"""
Jira API project.
Able to work with jira using cli and UI.
User is able to upload files see comments track issues and many more..
See comments in each function
"""
from jira import JIRA
from jira import JIRAError
from jira import *
import os
import webbrowser
import threading
from cryptography.fernet import Fernet
from win10toast import ToastNotifier

list_of_issues = []


def read_key():
    with open("key.txt", 'r') as f:
        key = f.readline()
        f.close()
        return key


def reading_file(file):
    with open(file, 'rb') as f:
        encrypted = f.readline()
        f.close()
        return encrypted


def writing_file(credentials, file):
    with open(file, 'wb') as f:
        f.write(credentials)
        f.close()


def setting_username_password():
    """ checking if password and username files are present in script location.
    if exists reading the file and returning plain password and username to jira_auth function.
    if it doesnt exists asking user to enter his jira username and password.
    encrypting both with encryption key and returning plain username password ti jira_auth
    function being called by jira_auth"""
    encryption_key = read_key()
    encryption_key = encryption_key.encode()
    encryption_key = bytes(encryption_key)
    username = 'None'
    password = 'None'
    password_file = 'Password.ini'
    username_file = 'username.ini'
    # checking if configue file exists
    if os.path.isfile(password_file and username_file):
        pass_encry = reading_file(password_file)
        username_encry = reading_file(username_file)
        f = Fernet(key=encryption_key)
        username = f.decrypt(username_encry)
        password = f.decrypt(pass_encry)
        return username, password
    else:
        # Getting user input for his username password
        print('before stating using program need to choose a valid username passowrd')
        print('no username password was set for jira please set one now\n')
        username = input('please enter your username: ')
        password = input('plaese enter your password: ')
        choice = input('would you like to set a "remember me" Y/N: ')
        if choice == 'Y' or choice == 'y':
            # encrypting password
            username_encoded = username.encode()
            password_encoded = password.encode()
            f = Fernet(key=encryption_key)
            encrypted_user = f.encrypt(username_encoded)
            encrypted_password = f.encrypt(password_encoded)
            # creating file for username password
            writing_file(encrypted_password, password_file)
            writing_file(encrypted_user, username_file)
        else:
            pass
        return username, password


def jira_auth():
    """trying to decode username password else password already plain and authentication to jira.
     this is a core function and being called by main once"""
    username, passowrd = setting_username_password()
    # decoding the input as utf and requesting auth to jira
    try:
        username = username.decode("utf-8")
        passowrd = passowrd.decode("utf-8")
    except AttributeError:
        pass
    # jira = JIRA(#eneter jira website, auth=(username, passowrd))
    return jira


def manual():
    """setting menu and returning choice to main"""
    try:
        os.system('cls')
    except:
        os.system('clear')
    print("Welcome to Jira API!\n\nThe Bug createor and opener, the options:")
    print("1.To view a bug  - V")
    print("2.To leave a comment - G")
    print("3.Assign issue to user - A")
    print("4.Add attachments - K")
    print("5.Log tasks - l")
    print("6. To all unresolved issues for version - O")
    print("7. To view all issues assigned to user - S")
    print("8. To add issue to track - T")
    print("9. To remove issue to track - Q")
    print("10.To exit program - E")
    chocie = input("please enter choice: ")
    return chocie


def view_bug():
    # opening bug in jira
    not_valid = 0
    while not_valid == 0:
        global open_in_page, bug_num
        # Getting bug number from user
        bug = input("you chose to view a bug, please enter bug number: ")
        bug_num = bug
        try:
            # printing bug fields
            bug = jira.issue(bug)
            print("\n By hanlded by\n\n", bug.fields.assignee.displayName)
            print("\nBug reproter\n\n", bug.fields.reporter.displayName)
            print("\nBug status\n\n", bug.fields.status)
            print("\nBug summary\n\n", bug.fields.summary)
            print("\nBug description\n\n", bug.fields.description)
            print("\nComment bugs - ")
            comments = jira.comments(bug)
            for i in comments:
                # printing every comment in bug
                print(jira.comment(issue=bug, comment=i).author.name)
                print(jira.comment(issue=bug, comment=i).body)
                print("\n\n")
            open_in_page = input("Do you want to open issue in webpage Y/N: ")
            not_valid = 1
        except JIRAError as e:
            if 'Exist' in e.text:
                # Checking if issue is valid
                print('The issue doesnt exists')
    if open_in_page == 'Y' or open_in_page == 'y':
        # asking user if he wants to open it in webpage
        base_url = "" #need to set base url
        url = base_url + bug_num
        webbrowser.open(url)
    else:
        # passing if answer is "No"
        pass


def leave_comment():
    # asking user to bug number and his comment.
    bug = input("you chose to comment a bug, please enter bug number: ")
    comment = input("Please enter you comment: ")
    try:
        # adding the comment to bug
        jira.add_comment(bug, comment)
        print("added comment" + comment)
    except JIRAError:
        # assuming wrong issue or no permissions
        print('No permissions or issue doesnt exists')


def log_tasks():
    # asking user to enter task number comment and time spent
    task = input("you chose to log a task, please enter task number: ")
    comment_to_leave = input("Please leave a comment : ")
    time_spent = input("how much time did you worked on this task :")
    try:
        jira.add_worklog(issue=task, timeSpent=time_spent, comment=comment_to_leave)
    except JIRAError:
        # expecting wrong issue has been added or no permissions
        print("No permissions or issue doesnt exists")


def assign_user():
    task = input("you chose to assign a task/bug, please enter task number : ")
    bug = task
    bug = jira.issue(bug)
    print("\n By hanlded by\n\n", bug.fields.assignee.displayName)
    user_name = input("Please enter jira username : ")
    jira.assign_issue(task, user_name)


def attach_files():
    task = input("you chose to attach a file to  task/bug, please enter task number : ")
    attachment = input("Please select the path for the attachments : ")
    try:
        jira.add_attachment(issue=task, attachment=attachment)
    except JIRAError:
        print("No permissions or issue doesnt exists")


def get_all_bugs():
    # getting all bugs in project and found version.
    # asking project and version found
    project = input("What Project is it (EPS/PMTR) : ")
    version = input("What version do you want to view : ")
    try:
        # trying to show all issues if fails
        jira_ver_issues = (
            jira.search_issues(
                jql_str=f"project='{project}' AND 'Found in Version'= {version} AND resolution = Unresolved ",
                maxResults=100))
        print(jira_ver_issues)
        for i in jira_ver_issues:
            print(f"\n{i}")
            bug = i.id
            bug = jira.issue(bug)
            print("Bug summary\n\n", bug.fields.summary)
            print("\nPlanned to be fixed in ", bug.fields.fixVersions)
        return False
    except JIRAError:
        print("Are you sure this is the right project or version? ")


def get_bugs_assigned_user():
    while True:
        print("View all Bugs assigned to you")
        # getting all issues assigned to current user and printing unresolved issues
        bugs_on_you = jira.search_issues(jql_str="assignee = currentuser() and resolution = Unresolved")
        for i in bugs_on_you:
            print(f"\n{i}")
            bug = i.id
            bug = jira.issue(bug)
            print("Bug summary\n\n", bug.fields.summary)
        # Waiting for user to enter if he finished watching issues
        exit = input("If you are done viewing the issue please Enter 'E' to move on :")
        if exit == 'e' or 'E':
            return False
        else:
            pass


class Compering_issues:
    """
    Class is responsible of keeping all status of bugs
    """

    def __init__(self, bug_number):
        self.raw_number = bug_number
        self.bug = jira.issue(bug_number)
        self.summery = self.bug.fields.summary
        self.description = self.bug.fields.description
        self.status = self.bug.fields.status

    def return_compare(self):
        """
         return all fields below to compare funcation
        """
        return self.summery, self.description, self.status

    def update(self):
        """
        Opens a thread every 60 secs that calls compare function
        if compare returns true updating current fields
        """
        if compare(self.raw_number):
            self.summery = self.bug.fields.summary
            self.description = self.bug.fields.description
            self.status = self.bug.fields.status


def issues_to_track():
    """
    add an issue to track
    """
    issue_to_add = input("Please type the issue to add : ")
    issues_to_add = Compering_issues(issue_to_add)
    list_of_issues.append(issues_to_add)


def compare(bug_number):
    """
    being called by the class and checking if current status is different than one in the class
    """
    for i in list_of_issues:
        summery, description, status = i.return_compare()
        bug = jira.issue(bug_number)
        current_sum = bug.fields.summary
        current_descr = bug.fields.description
        current_status = bug.fields.status
        status = str(status)
        current_status = str(current_status)
        if current_sum != summery:
            notification("Changed summery")
            return True
        if current_descr != description:
            notification("Changed description")
            return True
        if status in current_status:
            pass
        else:
            notification('changed status')
            return True
    return False


def notification(notification_type):
    """Function being called by comping issues
    Shows windows notification if issues changes based on notification type"""
    # path_for_ico = please select a path for ico file
    toast = ToastNotifier()
    toast.show_toast("Jira API Note", notification_type, duration=10, icon_path=path_for_ico)


def removing_issues():
    """Removes issues from list_of_issues_to_track"""
    print("Available  issues to remove")
    for i in list_of_issues:
        print(i + '\n')
    bug_to_del = input('Please enter the issue you what to remove')
    list_of_issues.remove(bug_to_del)


def going_over_issue():
    """ starting to compare issues"""
    for i in list_of_issues:
        i.update()


def main():
    """This is the main function.
     this faction waits for a value from manual() function and putting value in choice.
     checks in if value is valid, also main checks if issues to track list is not empty and n is not 0
     if both are true every 60 threads is being open from comparing issues()"""
    n = 0
    global jira
    jira = jira_auth()
    while True:
        choice = manual()
        if choice == 'V' or choice == 'v':
            view_bug()
        elif choice == 'G' or choice == 'g':
            leave_comment()
        elif choice == 'l' or choice == 'L':
            log_tasks()
        elif choice == 'k' or choice == 'K':
            attach_files()
        elif choice == 'A' or choice == 'a':
            assign_user()
        elif choice == 'E' or choice == 'e':
            print('thank you for using the program')
            exit()
        elif choice == 't' or choice == 'T':
            issues_to_track()
        elif choice == "O" or choice == "o":
            get_all_bugs()
        elif choice == "S" or choice == "s":
            get_bugs_assigned_user()
        else:
            print("Invalid choice ")
        if list_of_issues:
            threading.Timer(60.0, going_over_issue().start)


if __name__ == '__main__':
    main()
