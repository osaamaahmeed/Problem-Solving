#include <bits/stdc++.h>
using namespace std;

using ll = long long;

void osaamaahmeed()
{
    ios_base::sync_with_stdio(false), cin.tie(0), cout.tie(0);
    // #ifndef ONLINE_JUDGE
    //     freopen("input.txt", "r", stdin), freopen("output.txt", "w", stdout);
    // #endif
}

void solve()
{
    set<char> a;
    int n;
    cin >> n;
    string s;
    cin >> s;
    if (n < 26)
    {
        cout << "NO";
        return;
    }
    for (char i : s)
    {
        if (i >= 65 && i <= 90)
            a.insert(i += 32);
        else
            a.insert(i);
    }
    if (a.size() >= 26)
        cout << "YES" << "\n";
    else
        cout << "NO" << "\n";
}

int main()
{
    osaamaahmeed();
    int t = 1;
    // cin >> t;

    while (t--)
        solve();
}

// ------------------------------------------------------------
// CF-520A — Pangram
// https://codeforces.com/problemset/problem/520/A
// Sources:
// Went:    (easy | struggled | hint | editorial)
// Insight:
