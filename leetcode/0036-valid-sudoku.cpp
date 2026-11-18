// LC-36 — Source: NeetCode 150 (Arrays & Hashing)
/* Notes:
We need to check for 3 things:

1. if (1-9) is repeated in a row:
- loop over the borad board[i][j]

2. if (1-9) is repeated in a column
- loop over the borad board[j][i]

3. if (1-9) is repeated in a 3x3 box
- loop every 3 cells in i and j
    - loop inside on each cell in the box

Time Complixty: O(1)
becase we already know the limit of the 2D matrix which is 9x9

need optimization in sapce
*/

#include <bits/stdc++.h>
using namespace std;

bool isValidSudoku(vector<vector<char>> &board)
{
    for (int i = 0; i < 9; i++)
    {
        set<char> check;
        for (int j = 0; j < 9; j++)
        {
            if (board[i][j] != '.')
            {
                if (check.count(board[i][j]))
                    return 0;
                else
                    check.insert(board[i][j]);
            }
        }
    }
    for (int i = 0; i < 9; i++)
    {
        set<char> check;
        for (int j = 0; j < 9; j++)
        {
            if (board[j][i] != '.')
            {
                if (check.count(board[j][i]))
                    return 0;
                else
                    check.insert(board[j][i]);
            }
        }
    }

    for (int i = 0; i < 9; i += 3)
    {
        for (int j = 0; j < 9; j += 3)
        {
            set<char> check;
            for (int x = 0; x < 3; x++)
            {
                for (int y = 0; y < 3; y++) {
                    if (board[i+x][j+y] != '.') {
                        if (check.count(board[i+x][j+y])) return 0;
                        else check.insert(board[i+x][j+y]);
                    } 
                }
            }
        }
    }
    return 1;
}

int main()
{
    vector<vector<char>> a = {
        {'8', '3', '.', '.', '7', '.', '.', '.', '.'},
        {'6', '.', '.', '1', '9', '5', '.', '.', '.'},
        {'.', '9', '8', '.', '.', '.', '.', '6', '.'},
        {'8', '.', '.', '.', '6', '.', '.', '.', '3'},
        {'4', '.', '.', '8', '.', '3', '.', '.', '1'},
        {'7', '.', '.', '.', '2', '.', '.', '.', '6'},
        {'.', '6', '.', '.', '.', '.', '2', '8', '.'},
        {'.', '.', '.', '4', '1', '9', '.', '.', '5'},
        {'.', '.', '.', '.', '8', '.', '.', '7', '9'}
    };

    cout << isValidSudoku(a);
}