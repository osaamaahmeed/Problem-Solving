#include <bits/stdc++.h>
using namespace std;

int minAddToMakeValid(string s)
{
    stack<char> a;
    for (int i = 0; i < s.size(); i++)
    {
        if (!a.empty())
        {
            if (s[i] == ')' && a.top() == '(')
            {
                a.pop();
                continue;
            }
                }
        a.push(s[i]);
    }
    return a.size();
}

// defualt parantheses problem

int main()
{
    cout << minAddToMakeValid("())");
    return 0;
}