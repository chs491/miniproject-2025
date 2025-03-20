#define _CRT_SECURE_NO_WARNINGS
#include <iostream>
#include <cstring>

using namespace std;
const int NAME_LEN = 20;

void ShowMenu(void);
void MakeAccount(void);
void DepositMoney(void);
void WithDrawMoney(void);
void ShowAllAccInfo(void);

enum {MAKE = 1, DEPOSIT, WITHDRAW, INQUIRE, EXIT};

class Account {
private:
	int accID;
	int balance;
	char* cusName;
public:
	Account(int ID, int money, char* name) : accID(ID), balance(money) {
		cusName = new char[strlen(name) + 1];
		strcpy(cusName, name);
	}
	int GetAccID() { return accID; }

	void Deposit(int money) {
		balance += money;
	}

	int Withdraw(int money) {
		if (balance < money)
			return 0;
		balance -= money;
		return money;
	}
	void ShowAccInfo() {
		cout << "계좌 ID : " << accID << endl;
		cout << "이름 : " << cusName << endl;
		cout << "잔액 : " << balance << endl;
	}
	~Account() {
		delete[] cusName;
	}
};

Account* accArr[100];
int accNum = 0;

int main()
{
	int choice;

	while (1)
	{
		ShowMenu();
		cout << "선택 : ";
		cin >> choice;
		cout << endl;

		switch (choice)
		{
		case MAKE:
			MakeAccount();
			break;
		case DEPOSIT:
			DepositMoney();
			break;
		case WITHDRAW:
			WithDrawMoney();
			break;
		case INQUIRE:
			ShowAllAccInfo();
			break;
		case EXIT:
			for (int i = 0; i < accNum; i++)
				delete accArr[i];
			return 0;
		default:
			cout << "Illegal selection." << endl;
		}
	}
	return 0;
}

void ShowMenu(void) {
	cout << "-----MENU-----" << endl;
	cout << "1. 계좌개설" << endl;
	cout << "2. 입금" << endl;
	cout << "3. 출금" << endl;
	cout << "4. 계좌정보 전체 출력" << endl;
	cout << "5. 프로그램 종료" << endl;
}

void MakeAccount(void) {
	int id;
	char name[NAME_LEN];
	int balance;

	cout << "[계좌개설]" << endl;
	cout << "계좌 ID : " << endl; cin >> id;
	cout << "이름 : " << endl; cin >> name;
	cout << "입금액 : " << endl; cin >> balance;
	cout << endl;
	accArr[accNum++] = new Account(id, balance, name);
}

void DepositMoney(void){
	int money;
	int id;
	cout << "[입금]" << endl;
	cout << "계좌ID" << endl; cin >> id;
	cout << "입금액" << endl; cin >> money;

	for (int i = 0; i < accNum; i++) {
		if (accArr[i]->GetAccID() == id)
		{
			accArr[i]->Deposit(money);
			cout << "입금완료" << endl << endl;
			return;
		}
	}
	cout << "유효하지 않은 ID입니다." << endl << endl;
}

void WithDrawMoney(void) {
	int money;
	int id;
	cout << "[출금]" << endl;
	cout << "계좌ID" << endl; cin >> id;
	cout << "출금액" << endl; cin >> money;

	for (int i = 0; i < accNum; i++) {
		if (accArr[i]->GetAccID() == id)
		{
			if (accArr[i]->Withdraw(money) == 0)
			{
				cout << "잔액부족" << endl << endl;
			}
			cout << "출금완료" << endl << endl;
			return;
		}
	}
	cout << "유효하지 않은 ID입니다." << endl << endl;
}

void ShowAllAccInfo(void) {
	for (int i = 0; i < accNum; i++) {
		accArr[i]->ShowAccInfo();
		cout << endl;
	}
}