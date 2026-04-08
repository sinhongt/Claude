def add(a, b):
    return a + b


def subtract(a, b):
    return a - b


def main():
    print("=== 簡單計算機 ===")
    print("支援操作: 加法 (+), 減法 (-)")
    print("輸入 'q' 退出\n")

    while True:
        try:
            first = input("輸入第一個數字: ")
            if first.lower() == 'q':
                break
            a = float(first)

            op = input("輸入操作 (+ 或 -): ").strip()
            if op.lower() == 'q':
                break
            if op not in ('+', '-'):
                print("無效操作，請輸入 + 或 -\n")
                continue

            second = input("輸入第二個數字: ")
            if second.lower() == 'q':
                break
            b = float(second)

            if op == '+':
                result = add(a, b)
                symbol = '+'
            else:
                result = subtract(a, b)
                symbol = '-'

            print(f"結果: {a} {symbol} {b} = {result}\n")

        except ValueError:
            print("無效輸入，請輸入數字\n")

    print("再見！")


if __name__ == "__main__":
    main()
