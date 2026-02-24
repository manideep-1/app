"""
Supplemental code_java, code_cpp, code_c for solution approaches.
Key: (problem_title, approach_title_lower) -> {code_java?, code_cpp?, code_c?}.
Every approach should have real code in all 5 languages (no placeholders).
"""

def _key(problem: str, approach_title: str) -> tuple:
    return (problem.strip(), (approach_title or "").strip().lower())

# (problem_title, approach_title_lower) -> {code_java, code_cpp, code_c}
MULTILANG = {
    ("Two Sum", "1. brute force"): {
        "code_c": "int* twoSum(int* nums, int n, int target, int* returnSize) {\n    *returnSize = 2;\n    int* out = (int*)malloc(2 * sizeof(int));\n    for (int i = 0; i < n; i++)\n        for (int j = i + 1; j < n; j++)\n            if (nums[i] + nums[j] == target) { out[0] = i; out[1] = j; return out; }\n    return out;\n}",
    },
    ("Two Sum", "2. optimal (hash map)"): {
        "code_c": "int* twoSum(int* nums, int n, int target, int* returnSize) {\n    *returnSize = 2;\n    int* out = (int*)malloc(2 * sizeof(int));\n    for (int i = 0; i < n; i++) {\n        int need = target - nums[i];\n        for (int j = 0; j < i; j++) if (nums[j] == need) { out[0] = j; out[1] = i; return out; }\n    }\n    return out;\n}",
    },
    ("Valid Palindrome", "brute force"): {
        "code_java": "public boolean isPalindrome(String s) {\n    StringBuilder sb = new StringBuilder();\n    for (char c : s.toCharArray()) if (Character.isLetterOrDigit(c)) sb.append(Character.toLowerCase(c));\n    String t = sb.toString();\n    return t.equals(new StringBuilder(t).reverse().toString());\n}",
        "code_cpp": "bool isPalindrome(string s) {\n    string t;\n    for (char c : s) if (isalnum(c)) t += tolower(c);\n    string r = t; reverse(r.begin(), r.end());\n    return t == r;\n}",
        "code_c": "bool isPalindrome(char* s) {\n    char t[200001]; int len = 0;\n    for (; *s; s++) if (isalnum((unsigned char)*s)) t[len++] = tolower((unsigned char)*s);\n    t[len] = '\\0';\n    for (int i = 0, j = len-1; i < j; i++, j--) if (t[i] != t[j]) return false;\n    return true;\n}",
    },
    ("Valid Palindrome", "optimal (two pointers)"): {
        "code_java": "public boolean isPalindrome(String s) {\n    int i = 0, j = s.length() - 1;\n    while (i < j) {\n        if (!Character.isLetterOrDigit(s.charAt(i))) { i++; continue; }\n        if (!Character.isLetterOrDigit(s.charAt(j))) { j--; continue; }\n        if (Character.toLowerCase(s.charAt(i)) != Character.toLowerCase(s.charAt(j))) return false;\n        i++; j--;\n    }\n    return true;\n}",
        "code_cpp": "bool isPalindrome(string s) {\n    int i = 0, j = s.size() - 1;\n    while (i < j) {\n        if (!isalnum(s[i])) { i++; continue; }\n        if (!isalnum(s[j])) { j--; continue; }\n        if (tolower(s[i]) != tolower(s[j])) return false;\n        i++; j--;\n    }\n    return true;\n}",
        "code_c": "bool isPalindrome(char* s) {\n    int i = 0, j = strlen(s) - 1;\n    while (i < j) {\n        if (!isalnum((unsigned char)s[i])) { i++; continue; }\n        if (!isalnum((unsigned char)s[j])) { j--; continue; }\n        if (tolower((unsigned char)s[i]) != tolower((unsigned char)s[j])) return false;\n        i++; j--;\n    }\n    return true;\n}",
    },
    ("Product of Array Except Self", "brute force"): {
        "code_java": "public int[] productExceptSelf(int[] nums) {\n    int n = nums.length;\n    int[] out = new int[n];\n    for (int i = 0; i < n; i++) {\n        int p = 1;\n        for (int j = 0; j < n; j++) if (i != j) p *= nums[j];\n        out[i] = p;\n    }\n    return out;\n}",
        "code_cpp": "vector<int> productExceptSelf(vector<int>& nums) {\n    int n = nums.size();\n    vector<int> out(n);\n    for (int i = 0; i < n; i++) {\n        int p = 1;\n        for (int j = 0; j < n; j++) if (i != j) p *= nums[j];\n        out[i] = p;\n    }\n    return out;\n}",
        "code_c": "int* productExceptSelf(int* nums, int n, int* returnSize) {\n    *returnSize = n;\n    int* out = (int*)malloc(n * sizeof(int));\n    for (int i = 0; i < n; i++) {\n        int p = 1;\n        for (int j = 0; j < n; j++) if (i != j) p *= nums[j];\n        out[i] = p;\n    }\n    return out;\n}",
    },
    ("Product of Array Except Self", "optimal (prefix × suffix)"): {
        "code_java": "public int[] productExceptSelf(int[] nums) {\n    int n = nums.length;\n    int[] out = new int[n];\n    int p = 1;\n    for (int i = 0; i < n; i++) { out[i] = p; p *= nums[i]; }\n    p = 1;\n    for (int i = n - 1; i >= 0; i--) { out[i] *= p; p *= nums[i]; }\n    return out;\n}",
        "code_cpp": "vector<int> productExceptSelf(vector<int>& nums) {\n    int n = nums.size();\n    vector<int> out(n);\n    int p = 1;\n    for (int i = 0; i < n; i++) { out[i] = p; p *= nums[i]; }\n    p = 1;\n    for (int i = n - 1; i >= 0; i--) { out[i] *= p; p *= nums[i]; }\n    return out;\n}",
        "code_c": "int* productExceptSelf(int* nums, int n, int* returnSize) {\n    *returnSize = n;\n    int* out = (int*)malloc(n * sizeof(int));\n    int p = 1;\n    for (int i = 0; i < n; i++) { out[i] = p; p *= nums[i]; }\n    p = 1;\n    for (int i = n - 1; i >= 0; i--) { out[i] *= p; p *= nums[i]; }\n    return out;\n}",
    },
    ("3Sum", "brute force"): {
        "code_java": "public List<List<Integer>> threeSum(int[] nums) {\n    Arrays.sort(nums);\n    Set<List<Integer>> set = new HashSet<>();\n    int n = nums.length;\n    for (int i = 0; i < n; i++)\n        for (int j = i+1; j < n; j++)\n            for (int k = j+1; k < n; k++)\n                if (nums[i]+nums[j]+nums[k] == 0)\n                    set.add(Arrays.asList(nums[i], nums[j], nums[k]));\n    return new ArrayList<>(set);\n}",
        "code_cpp": "vector<vector<int>> threeSum(vector<int>& nums) {\n    sort(nums.begin(), nums.end());\n    set<vector<int>> st;\n    int n = nums.size();\n    for (int i = 0; i < n; i++)\n        for (int j = i+1; j < n; j++)\n            for (int k = j+1; k < n; k++)\n                if (nums[i]+nums[j]+nums[k] == 0)\n                    st.insert({nums[i], nums[j], nums[k]});\n    return vector<vector<int>>(st.begin(), st.end());\n}",
        "code_c": "int cmp(const void* a, const void* b) { return *(int*)a - *(int*)b; }\nint** threeSum(int* nums, int n, int* returnSize, int** returnColumnSizes) {\n    qsort(nums, n, sizeof(int), cmp);\n    int** res = (int**)malloc(20000*sizeof(int*));\n    int sz = 0;\n    for (int i = 0; i < n; i++)\n        for (int j = i+1; j < n; j++)\n            for (int k = j+1; k < n; k++)\n                if (nums[i]+nums[j]+nums[k] == 0) {\n                    res[sz] = (int*)malloc(3*sizeof(int));\n                    res[sz][0]=nums[i]; res[sz][1]=nums[j]; res[sz][2]=nums[k];\n                    sz++;\n                }\n    *returnSize = sz;\n    *returnColumnSizes = (int*)malloc(sz*sizeof(int));\n    for (int i = 0; i < sz; i++) (*returnColumnSizes)[i] = 3;\n    return res;\n}",
    },
    ("3Sum", "optimal (sort + two pointers)"): {
        "code_java": "public List<List<Integer>> threeSum(int[] nums) {\n    Arrays.sort(nums);\n    List<List<Integer>> res = new ArrayList<>();\n    for (int i = 0; i < nums.length; i++) {\n        if (i > 0 && nums[i] == nums[i-1]) continue;\n        int l = i+1, r = nums.length - 1;\n        while (l < r) {\n            int s = nums[i] + nums[l] + nums[r];\n            if (s == 0) { res.add(Arrays.asList(nums[i], nums[l], nums[r])); l++; while (l < r && nums[l] == nums[l-1]) l++; }\n            else if (s < 0) l++; else r--;\n        }\n    }\n    return res;\n}",
        "code_cpp": "vector<vector<int>> threeSum(vector<int>& nums) {\n    sort(nums.begin(), nums.end());\n    vector<vector<int>> res;\n    for (int i = 0; i < (int)nums.size(); i++) {\n        if (i && nums[i] == nums[i-1]) continue;\n        int l = i+1, r = nums.size() - 1;\n        while (l < r) {\n            int s = nums[i] + nums[l] + nums[r];\n            if (s == 0) { res.push_back({nums[i], nums[l], nums[r]}); l++; while (l < r && nums[l] == nums[l-1]) l++; }\n            else if (s < 0) l++; else r--;\n        }\n    }\n    return res;\n}",
        "code_c": "int cmp(const void* a, const void* b) { return *(int*)a - *(int*)b; }\nint** threeSum(int* nums, int n, int* returnSize, int** returnColumnSizes) {\n    qsort(nums, n, sizeof(int), cmp);\n    int** res = (int**)malloc(20000*sizeof(int*));\n    int sz = 0;\n    for (int i = 0; i < n; i++) {\n        if (i > 0 && nums[i] == nums[i-1]) continue;\n        int l = i+1, r = n-1;\n        while (l < r) {\n            int s = nums[i] + nums[l] + nums[r];\n            if (s == 0) {\n                res[sz] = (int*)malloc(3*sizeof(int));\n                res[sz][0]=nums[i]; res[sz][1]=nums[l]; res[sz][2]=nums[r]; sz++;\n                l++; while (l < r && nums[l] == nums[l-1]) l++;\n            } else if (s < 0) l++; else r--;\n        }\n    }\n    *returnSize = sz;\n    *returnColumnSizes = (int*)malloc(sz*sizeof(int));\n    for (int i = 0; i < sz; i++) (*returnColumnSizes)[i] = 3;\n    return res;\n}",
    },
    ("Maximum Product Subarray", "brute force"): {
        "code_java": "public int maxProduct(int[] nums) {\n    int best = nums[0];\n    for (int i = 0; i < nums.length; i++) {\n        int p = 1;\n        for (int j = i; j < nums.length; j++) { p *= nums[j]; best = Math.max(best, p); }\n    }\n    return best;\n}",
        "code_cpp": "int maxProduct(vector<int>& nums) {\n    int best = nums[0];\n    for (int i = 0; i < (int)nums.size(); i++) {\n        int p = 1;\n        for (int j = i; j < (int)nums.size(); j++) { p *= nums[j]; best = max(best, p); }\n    }\n    return best;\n}",
        "code_c": "int maxProduct(int* nums, int n) {\n    int best = nums[0];\n    for (int i = 0; i < n; i++) {\n        int p = 1;\n        for (int j = i; j < n; j++) { p *= nums[j]; if (p > best) best = p; }\n    }\n    return best;\n}",
    },
    ("Maximum Product Subarray", "optimal (track max and min)"): {
        "code_java": "public int maxProduct(int[] nums) {\n    int curMax = nums[0], curMin = nums[0], best = nums[0];\n    for (int i = 1; i < nums.length; i++) {\n        int x = nums[i], a = curMax * x, b = curMin * x;\n        curMax = Math.max(x, Math.max(a, b));\n        curMin = Math.min(x, Math.min(a, b));\n        best = Math.max(best, curMax);\n    }\n    return best;\n}",
        "code_cpp": "int maxProduct(vector<int>& nums) {\n    int curMax = nums[0], curMin = nums[0], best = nums[0];\n    for (int i = 1; i < (int)nums.size(); i++) {\n        int x = nums[i], a = curMax * x, b = curMin * x;\n        curMax = max(x, max(a, b));\n        curMin = min(x, min(a, b));\n        best = max(best, curMax);\n    }\n    return best;\n}",
        "code_c": "int maxProduct(int* nums, int n) {\n    int curMax = nums[0], curMin = nums[0], best = nums[0];\n    for (int i = 1; i < n; i++) {\n        int x = nums[i], a = curMax*x, b = curMin*x;\n        curMax = (x > a && x > b) ? x : (a > b ? a : b);\n        curMin = (x < a && x < b) ? x : (a < b ? a : b);\n        if (curMax > best) best = curMax;\n    }\n    return best;\n}",
    },
    ("Container With Most Water", "brute force"): {
        "code_java": "public int maxArea(int[] height) {\n    int best = 0;\n    for (int i = 0; i < height.length; i++)\n        for (int j = i+1; j < height.length; j++)\n            best = Math.max(best, Math.min(height[i], height[j]) * (j - i));\n    return best;\n}",
        "code_cpp": "int maxArea(vector<int>& height) {\n    int best = 0;\n    for (int i = 0; i < (int)height.size(); i++)\n        for (int j = i+1; j < (int)height.size(); j++)\n            best = max(best, min(height[i], height[j]) * (j - i));\n    return best;\n}",
        "code_c": "int maxArea(int* height, int n) {\n    int best = 0;\n    for (int i = 0; i < n; i++)\n        for (int j = i+1; j < n; j++) {\n            int area = (height[i] < height[j] ? height[i] : height[j]) * (j - i);\n            if (area > best) best = area;\n        }\n    return best;\n}",
    },
    ("Container With Most Water", "optimal (two pointers)"): {
        "code_java": "public int maxArea(int[] height) {\n    int l = 0, r = height.length - 1, best = 0;\n    while (l < r) {\n        best = Math.max(best, Math.min(height[l], height[r]) * (r - l));\n        if (height[l] < height[r]) l++; else r--;\n    }\n    return best;\n}",
        "code_cpp": "int maxArea(vector<int>& height) {\n    int l = 0, r = height.size() - 1, best = 0;\n    while (l < r) {\n        best = max(best, min(height[l], height[r]) * (r - l));\n        if (height[l] < height[r]) l++; else r--;\n    }\n    return best;\n}",
        "code_c": "int maxArea(int* height, int n) {\n    int l = 0, r = n - 1, best = 0;\n    while (l < r) {\n        int area = (height[l] < height[r] ? height[l] : height[r]) * (r - l);\n        if (area > best) best = area;\n        if (height[l] < height[r]) l++; else r--;\n    }\n    return best;\n}",
    },
    ("Longest Substring Without Repeating Characters", "brute force"): {
        "code_java": "public int lengthOfLongestSubstring(String s) {\n    int best = 0;\n    for (int i = 0; i < s.length(); i++)\n        for (int j = i + 1; j <= s.length(); j++) {\n            Set<Character> set = new HashSet<>();\n            boolean ok = true;\n            for (int k = i; k < j && ok; k++) if (!set.add(s.charAt(k))) ok = false;\n            if (ok) best = Math.max(best, j - i);\n        }\n    return best;\n}",
        "code_cpp": "int lengthOfLongestSubstring(string s) {\n    int best = 0;\n    for (int i = 0; i < (int)s.size(); i++)\n        for (int j = i + 1; j <= (int)s.size(); j++) {\n            set<char> st(s.begin()+i, s.begin()+j);\n            if ((int)st.size() == j - i) best = max(best, j - i);\n        }\n    return best;\n}",
        "code_c": "int lengthOfLongestSubstring(char* s) {\n    int best = 0, n = strlen(s);\n    for (int i = 0; i < n; i++)\n        for (int j = i + 1; j <= n; j++) {\n            int seen[128] = {0}, ok = 1;\n            for (int k = i; k < j && ok; k++) { if (seen[(unsigned)s[k]]) ok = 0; seen[(unsigned)s[k]] = 1; }\n            if (ok && j - i > best) best = j - i;\n        }\n    return best;\n}",
    },
    ("Longest Substring Without Repeating Characters", "optimal (sliding window + set)"): {
        "code_java": "public int lengthOfLongestSubstring(String s) {\n    Set<Character> seen = new HashSet<>();\n    int left = 0, best = 0;\n    for (int right = 0; right < s.length(); right++) {\n        while (seen.contains(s.charAt(right))) { seen.remove(s.charAt(left)); left++; }\n        seen.add(s.charAt(right));\n        best = Math.max(best, right - left + 1);\n    }\n    return best;\n}",
        "code_cpp": "int lengthOfLongestSubstring(string s) {\n    unordered_set<char> seen;\n    int left = 0, best = 0;\n    for (int right = 0; right < (int)s.size(); right++) {\n        while (seen.count(s[right])) { seen.erase(s[left]); left++; }\n        seen.insert(s[right]);\n        best = max(best, right - left + 1);\n    }\n    return best;\n}",
        "code_c": "int lengthOfLongestSubstring(char* s) {\n    int seen[128] = {0}, left = 0, best = 0;\n    for (int right = 0; s[right]; right++) {\n        while (seen[(unsigned)s[right]]) seen[(unsigned)s[left++]] = 0;\n        seen[(unsigned)s[right]] = 1;\n        if (right - left + 1 > best) best = right - left + 1;\n    }\n    return best;\n}",
    },
    ("Longest Palindromic Substring", "brute force"): {
        "code_java": "public String longestPalindrome(String s) {\n    String best = \"\";\n    for (int i = 0; i < s.length(); i++)\n        for (int j = i; j < s.length(); j++) {\n            String sub = s.substring(i, j+1);\n            if (new StringBuilder(sub).reverse().toString().equals(sub) && sub.length() > best.length()) best = sub;\n        }\n    return best;\n}",
        "code_cpp": "string longestPalindrome(string s) {\n    string best = \"\";\n    for (int i = 0; i < (int)s.size(); i++)\n        for (int j = i; j < (int)s.size(); j++) {\n            string sub = s.substr(i, j-i+1);\n            string r = sub; reverse(r.begin(), r.end());\n            if (sub == r && (int)sub.size() > (int)best.size()) best = sub;\n        }\n    return best;\n}",
        "code_c": "int isPal(char* s, int i, int j) {\n    while (i < j) if (s[i++] != s[j--]) return 0; return 1;\n}\nchar* longestPalindrome(char* s) {\n    int n = strlen(s), maxLen = 0, start = 0;\n    for (int i = 0; i < n; i++)\n        for (int j = i; j < n; j++)\n            if (isPal(s,i,j) && j-i+1 > maxLen) { maxLen = j-i+1; start = i; }\n    s[start+maxLen] = '\\0'; return s+start;\n}",
    },
    ("Longest Palindromic Substring", "optimal (expand around center)"): {
        "code_java": "public String longestPalindrome(String s) {\n    String best = \"\";\n    for (int i = 0; i < s.length(); i++) {\n        for (int d = 0; d <= 1; d++) {\n            int l = i, r = i + d;\n            while (l >= 0 && r < s.length() && s.charAt(l) == s.charAt(r)) { l--; r++; }\n            String cand = s.substring(l+1, r);\n            if (cand.length() > best.length()) best = cand;\n        }\n    }\n    return best;\n}",
        "code_cpp": "string longestPalindrome(string s) {\n    string best = \"\";\n    for (int i = 0; i < (int)s.size(); i++)\n        for (int d = 0; d <= 1; d++) {\n            int l = i, r = i + d;\n            while (l >= 0 && r < (int)s.size() && s[l] == s[r]) { l--; r++; }\n            if (r - l - 1 > (int)best.size()) best = s.substr(l+1, r-l-1);\n        }\n    return best;\n}",
        "code_c": "int expand(char* s, int n, int l, int r) {\n    while (l >= 0 && r < n && s[l] == s[r]) { l--; r++; }\n    return r - l - 1;\n}\nchar* longestPalindrome(char* s) {\n    int n = strlen(s), maxLen = 0, start = 0;\n    for (int i = 0; i < n; i++)\n        for (int d = 0; d <= 1; d++) {\n            int len = expand(s, n, i, i+d);\n            if (len > maxLen) { maxLen = len; start = i - (len-1)/2; }\n        }\n    s[start+maxLen] = '\\0'; return s+start;\n}",
    },
    ("Climbing Stairs", "brute force (recursion)"): {
        "code_java": "public int climbStairs(int n) {\n    if (n <= 2) return n;\n    return climbStairs(n-1) + climbStairs(n-2);\n}",
        "code_cpp": "int climbStairs(int n) {\n    if (n <= 2) return n;\n    return climbStairs(n-1) + climbStairs(n-2);\n}",
        "code_c": "int climbStairs(int n) {\n    if (n <= 2) return n;\n    return climbStairs(n-1) + climbStairs(n-2);\n}",
    },
    ("Climbing Stairs", "optimal (dp / fibonacci)"): {
        "code_java": "public int climbStairs(int n) {\n    if (n <= 2) return n;\n    int prev = 1, curr = 2;\n    for (int i = 3; i <= n; i++) { int next = prev + curr; prev = curr; curr = next; }\n    return curr;\n}",
        "code_cpp": "int climbStairs(int n) {\n    if (n <= 2) return n;\n    int prev = 1, curr = 2;\n    for (int i = 3; i <= n; i++) { int next = prev + curr; prev = curr; curr = next; }\n    return curr;\n}",
        "code_c": "int climbStairs(int n) {\n    if (n <= 2) return n;\n    int prev = 1, curr = 2;\n    for (int i = 3; i <= n; i++) { int next = prev + curr; prev = curr; curr = next; }\n    return curr;\n}",
    },
    ("House Robber", "brute force (recursion)"): {
        "code_java": "public int rob(int[] nums) {\n    return rob(nums, nums.length - 1);\n}\nint rob(int[] nums, int i) {\n    if (i < 0) return 0;\n    return Math.max(nums[i] + rob(nums, i-2), rob(nums, i-1));\n}",
        "code_cpp": "int rob(vector<int>& nums, int i) {\n    if (i < 0) return 0;\n    return max(nums[i] + rob(nums, i-2), rob(nums, i-1));\n}\nint rob(vector<int>& nums) { return rob(nums, nums.size()-1); }",
        "code_c": "int rob(int* nums, int n, int i) {\n    if (i < 0) return 0;\n    int a = nums[i] + rob(nums, n, i-2), b = rob(nums, n, i-1);\n    return a > b ? a : b;\n}\nint rob(int* nums, int n) { return n ? rob(nums, n, n-1) : 0; }",
    },
    ("House Robber", "optimal (dp)"): {
        "code_java": "public int rob(int[] nums) {\n    int prev = 0, curr = 0;\n    for (int x : nums) { int next = Math.max(curr, prev + x); prev = curr; curr = next; }\n    return curr;\n}",
        "code_cpp": "int rob(vector<int>& nums) {\n    int prev = 0, curr = 0;\n    for (int x : nums) { int next = max(curr, prev + x); prev = curr; curr = next; }\n    return curr;\n}",
        "code_c": "int rob(int* nums, int n) {\n    int prev = 0, curr = 0;\n    for (int i = 0; i < n; i++) { int next = (curr > prev + nums[i]) ? curr : prev + nums[i]; prev = curr; curr = next; }\n    return curr;\n}",
    },
    ("Group Anagrams", "brute force"): {
        "code_java": "public List<List<String>> groupAnagrams(String[] strs) {\n    Map<String, List<String>> map = new HashMap<>();\n    for (String s : strs) {\n        char[] a = s.toCharArray(); Arrays.sort(a);\n        String key = String.valueOf(a);\n        map.computeIfAbsent(key, k -> new ArrayList<>()).add(s);\n    }\n    return new ArrayList<>(map.values());\n}",
        "code_cpp": "vector<vector<string>> groupAnagrams(vector<string>& strs) {\n    map<string, vector<string>> mp;\n    for (auto& s : strs) { string k = s; sort(k.begin(), k.end()); mp[k].push_back(s); }\n    vector<vector<string>> res;\n    for (auto& p : mp) res.push_back(p.second);\n    return res;\n}",
        "code_c": "int cmp(const void* a, const void* b) { return *(char*)a - *(char*)b; }\nchar*** groupAnagrams(char** strs, int n, int* outSz, int** colSizes) {\n    char** keys = (char**)malloc(n*sizeof(char*));\n    for (int i = 0; i < n; i++) { keys[i] = strdup(strs[i]); qsort(keys[i], strlen(keys[i]), 1, cmp); }\n    int* grp = (int*)malloc(n*sizeof(int)); int ng = 0;\n    for (int i = 0; i < n; i++) { int j = 0; while (j < ng && strcmp(keys[grp[j]], keys[i])) j++; if (j == ng) grp[ng++] = i; }\n    *outSz = ng; *colSizes = (int*)malloc(ng*sizeof(int));\n    char*** res = (char***)malloc(ng*sizeof(char**));\n    for (int g = 0; g < ng; g++) { int cnt = 0; for (int i = 0; i < n; i++) if (!strcmp(keys[i], keys[grp[g]])) cnt++; (*colSizes)[g]=cnt; res[g]=(char**)malloc(cnt*sizeof(char*)); int k=0; for (int i=0;i<n;i++) if (!strcmp(keys[i],keys[grp[g]])) res[g][k++]=strs[i]; }\n    return res;\n}",
    },
    ("Group Anagrams", "optimal (hash by sorted string or count)"): {
        "code_java": "public List<List<String>> groupAnagrams(String[] strs) {\n    Map<String, List<String>> map = new HashMap<>();\n    for (String s : strs) {\n        int[] cnt = new int[26];\n        for (char c : s.toCharArray()) cnt[c-'a']++;\n        String key = Arrays.toString(cnt);\n        map.computeIfAbsent(key, k -> new ArrayList<>()).add(s);\n    }\n    return new ArrayList<>(map.values());\n}",
        "code_cpp": "vector<vector<string>> groupAnagrams(vector<string>& strs) {\n    map<string, vector<string>> mp;\n    for (auto& s : strs) {\n        int cnt[26] = {};\n        for (char c : s) cnt[c-'a']++;\n        string key; for (int i = 0; i < 26; i++) key += to_string(cnt[i]) + \",\";\n        mp[key].push_back(s);\n    }\n    vector<vector<string>> res;\n    for (auto& p : mp) res.push_back(p.second);\n    return res;\n}",
        "code_c": "char*** groupAnagrams(char** strs, int n, int* outSz, int** colSizes) {\n    char keys[10000][100]; int cnts[10000][26] = {0};\n    for (int i = 0; i < n; i++) for (char* c = strs[i]; *c; c++) cnts[i][*c-'a']++;\n    int grp[10000], ng = 0;\n    for (int i = 0; i < n; i++) {\n        int j = 0; for (; j < ng; j++) { int eq = 1; for (int k = 0; k < 26 && eq; k++) if (cnts[i][k] != cnts[grp[j]][k]) eq = 0; if (eq) break; }\n        if (j == ng) grp[ng++] = i;\n    }\n    *outSz = ng; *colSizes = (int*)malloc(ng*sizeof(int));\n    char*** res = (char***)malloc(ng*sizeof(char**));\n    for (int g = 0; g < ng; g++) { int c = 0; for (int i = 0; i < n; i++) { int eq = 1; for (int k = 0; k < 26 && eq; k++) if (cnts[i][k] != cnts[grp[g]][k]) eq = 0; if (eq) c++; } (*colSizes)[g]=c; res[g]=(char**)malloc(c*sizeof(char*)); int k=0; for (int i=0;i<n;i++) { int eq=1; for (int t=0;t<26&&eq;t++) if (cnts[i][t]!=cnts[grp[g]][t]) eq=0; if (eq) res[g][k++]=strs[i]; } }\n    return res;\n}",
    },
    ("Single Number", "brute force"): {
        "code_java": "public int singleNumber(int[] nums) {\n    Map<Integer, Integer> map = new HashMap<>();\n    for (int x : nums) map.put(x, map.getOrDefault(x, 0) + 1);\n    for (int x : nums) if (map.get(x) == 1) return x;\n    return -1;\n}",
        "code_cpp": "int singleNumber(vector<int>& nums) {\n    unordered_map<int, int> m;\n    for (int x : nums) m[x]++;\n    for (int x : nums) if (m[x] == 1) return x;\n    return -1;\n}",
        "code_c": "int singleNumber(int* nums, int n) {\n    int max = nums[0], min = nums[0];\n    for (int i = 0; i < n; i++) { if (nums[i] > max) max = nums[i]; if (nums[i] < min) min = nums[i]; }\n    int range = max - min + 1;\n    int* cnt = (int*)calloc(range, sizeof(int));\n    for (int i = 0; i < n; i++) cnt[nums[i]-min]++;\n    for (int i = 0; i < n; i++) if (cnt[nums[i]-min] == 1) { int r = nums[i]; free(cnt); return r; }\n    return -1;\n}",
    },
    ("Single Number", "optimal (xor)"): {
        "code_java": "public int singleNumber(int[] nums) {\n    int res = 0;\n    for (int x : nums) res ^= x;\n    return res;\n}",
        "code_cpp": "int singleNumber(vector<int>& nums) {\n    int res = 0;\n    for (int x : nums) res ^= x;\n    return res;\n}",
        "code_c": "int singleNumber(int* nums, int n) {\n    int res = 0;\n    for (int i = 0; i < n; i++) res ^= nums[i];\n    return res;\n}",
    },
    ("Number of 1 Bits", "brute force"): {
        "code_java": "public int hammingWeight(int n) {\n    n &= 0xFFFFFFFFL;\n    int c = 0;\n    while (n != 0) { c += n & 1; n >>>= 1; }\n    return c;\n}",
        "code_cpp": "int hammingWeight(uint32_t n) {\n    int c = 0;\n    while (n) { c += n & 1; n >>= 1; }\n    return c;\n}",
        "code_c": "int hammingWeight(uint32_t n) {\n    int c = 0;\n    while (n) { c += n & 1; n >>= 1; }\n    return c;\n}",
    },
    ("Number of 1 Bits", "optimal (n & (n-1))"): {
        "code_java": "public int hammingWeight(int n) {\n    n &= 0xFFFFFFFFL;\n    int c = 0;\n    while (n != 0) { n &= n - 1; c++; }\n    return c;\n}",
        "code_cpp": "int hammingWeight(uint32_t n) {\n    int c = 0;\n    while (n) { n &= n - 1; c++; }\n    return c;\n}",
        "code_c": "int hammingWeight(uint32_t n) {\n    int c = 0;\n    while (n) { n &= n - 1; c++; }\n    return c;\n}",
    },
    ("Reverse Bits", "brute force"): {
        "code_java": "public int reverseBits(int n) {\n    int res = 0;\n    for (int i = 0; i < 32; i++) { res = (res << 1) | (n & 1); n >>>= 1; }\n    return res;\n}",
        "code_cpp": "uint32_t reverseBits(uint32_t n) {\n    uint32_t res = 0;\n    for (int i = 0; i < 32; i++) { res = (res << 1) | (n & 1); n >>= 1; }\n    return res;\n}",
        "code_c": "uint32_t reverseBits(uint32_t n) {\n    uint32_t res = 0;\n    for (int i = 0; i < 32; i++) { res = (res << 1) | (n & 1); n >>= 1; }\n    return res;\n}",
    },
    ("Reverse Bits", "optimal (same)"): {
        "code_java": "public int reverseBits(int n) {\n    int res = 0;\n    for (int i = 0; i < 32; i++) { res = (res << 1) | (n & 1); n >>>= 1; }\n    return res;\n}",
        "code_cpp": "uint32_t reverseBits(uint32_t n) {\n    uint32_t res = 0;\n    for (int i = 0; i < 32; i++) { res = (res << 1) | (n & 1); n >>= 1; }\n    return res;\n}",
        "code_c": "uint32_t reverseBits(uint32_t n) {\n    uint32_t res = 0;\n    for (int i = 0; i < 32; i++) { res = (res << 1) | (n & 1); n >>= 1; }\n    return res;\n}",
    },
    ("Missing Number", "brute force (sort)"): {
        "code_java": "public int missingNumber(int[] nums) {\n    Arrays.sort(nums);\n    for (int i = 0; i < nums.length; i++) if (nums[i] != i) return i;\n    return nums.length;\n}",
        "code_cpp": "int missingNumber(vector<int>& nums) {\n    sort(nums.begin(), nums.end());\n    for (int i = 0; i < (int)nums.size(); i++) if (nums[i] != i) return i;\n    return nums.size();\n}",
        "code_c": "int cmp(const void* a, const void* b) { return *(int*)a - *(int*)b; }\nint missingNumber(int* nums, int n) {\n    qsort(nums, n, sizeof(int), cmp);\n    for (int i = 0; i < n; i++) if (nums[i] != i) return i;\n    return n;\n}",
    },
    ("Missing Number", "optimal (sum or xor)"): {
        "code_java": "public int missingNumber(int[] nums) {\n    int n = nums.length;\n    int sum = n * (n + 1) / 2;\n    for (int x : nums) sum -= x;\n    return sum;\n}",
        "code_cpp": "int missingNumber(vector<int>& nums) {\n    int n = nums.size();\n    int sum = n * (n + 1) / 2;\n    for (int x : nums) sum -= x;\n    return sum;\n}",
        "code_c": "int missingNumber(int* nums, int n) {\n    int sum = n * (n + 1) / 2;\n    for (int i = 0; i < n; i++) sum -= nums[i];\n    return sum;\n}",
    },
    ("Remove Duplicates from Sorted Array", "brute force"): {
        "code_java": "public int removeDuplicates(int[] nums) {\n    Set<Integer> seen = new HashSet<>();\n    List<Integer> out = new ArrayList<>();\n    for (int x : nums) if (seen.add(x)) out.add(x);\n    for (int i = 0; i < out.size(); i++) nums[i] = out.get(i);\n    return out.size();\n}",
        "code_cpp": "int removeDuplicates(vector<int>& nums) {\n    set<int> seen;\n    vector<int> out;\n    for (int x : nums) if (seen.insert(x).second) out.push_back(x);\n    for (int i = 0; i < (int)out.size(); i++) nums[i] = out[i];\n    return out.size();\n}",
        "code_c": "int removeDuplicates(int* nums, int n) {\n    if (n == 0) return 0;\n    int out[30000], sz = 0, prev = nums[0] - 1;\n    for (int i = 0; i < n; i++) if (nums[i] != prev) { prev = nums[i]; out[sz++] = nums[i]; }\n    for (int i = 0; i < sz; i++) nums[i] = out[i];\n    return sz;\n}",
    },
    ("Remove Duplicates from Sorted Array", "optimal (two pointers in-place)"): {
        "code_java": "public int removeDuplicates(int[] nums) {\n    if (nums.length == 0) return 0;\n    int w = 1;\n    for (int i = 1; i < nums.length; i++) if (nums[i] != nums[w-1]) nums[w++] = nums[i];\n    return w;\n}",
        "code_cpp": "int removeDuplicates(vector<int>& nums) {\n    if (nums.empty()) return 0;\n    int w = 1;\n    for (int i = 1; i < (int)nums.size(); i++) if (nums[i] != nums[w-1]) nums[w++] = nums[i];\n    return w;\n}",
        "code_c": "int removeDuplicates(int* nums, int n) {\n    if (n == 0) return 0;\n    int w = 1;\n    for (int i = 1; i < n; i++) if (nums[i] != nums[w-1]) nums[w++] = nums[i];\n    return w;\n}",
    },
    ("Sort Colors", "brute force (sort)"): {
        "code_java": "public void sortColors(int[] nums) {\n    Arrays.sort(nums);\n}",
        "code_cpp": "void sortColors(vector<int>& nums) {\n    sort(nums.begin(), nums.end());\n}",
        "code_c": "int cmp(const void* a, const void* b) { return *(int*)a - *(int*)b; }\nvoid sortColors(int* nums, int n) {\n    qsort(nums, n, sizeof(int), cmp);\n}",
    },
    ("Sort Colors", "optimal (dutch national flag)"): {
        "code_java": "public void sortColors(int[] nums) {\n    int lo = 0, mid = 0, hi = nums.length - 1;\n    while (mid <= hi) {\n        if (nums[mid] == 0) { int t = nums[lo]; nums[lo++] = nums[mid]; nums[mid++] = t; }\n        else if (nums[mid] == 2) { int t = nums[hi]; nums[hi--] = nums[mid]; nums[mid] = t; }\n        else mid++;\n    }\n}",
        "code_cpp": "void sortColors(vector<int>& nums) {\n    int lo = 0, mid = 0, hi = nums.size() - 1;\n    while (mid <= hi) {\n        if (nums[mid] == 0) swap(nums[lo++], nums[mid++]);\n        else if (nums[mid] == 2) swap(nums[mid], nums[hi--]);\n        else mid++;\n    }\n}",
        "code_c": "void sortColors(int* nums, int n) {\n    int lo = 0, mid = 0, hi = n - 1;\n    while (mid <= hi) {\n        if (nums[mid] == 0) { int t = nums[lo]; nums[lo++] = nums[mid]; nums[mid++] = t; }\n        else if (nums[mid] == 2) { int t = nums[hi]; nums[hi--] = nums[mid]; nums[mid] = t; }\n        else mid++;\n    }\n}",
    },
    ("Search in Rotated Sorted Array", "brute force"): {
        "code_java": "public int search(int[] nums, int target) {\n    for (int i = 0; i < nums.length; i++) if (nums[i] == target) return i;\n    return -1;\n}",
        "code_cpp": "int search(vector<int>& nums, int target) {\n    for (int i = 0; i < (int)nums.size(); i++) if (nums[i] == target) return i;\n    return -1;\n}",
        "code_c": "int search(int* nums, int n, int target) {\n    for (int i = 0; i < n; i++) if (nums[i] == target) return i;\n    return -1;\n}",
    },
    ("Search in Rotated Sorted Array", "optimal (binary search)"): {
        "code_java": "public int search(int[] nums, int target) {\n    int lo = 0, hi = nums.length - 1;\n    while (lo <= hi) {\n        int mid = (lo + hi) / 2;\n        if (nums[mid] == target) return mid;\n        if (nums[lo] <= nums[mid]) {\n            if (nums[lo] <= target && target < nums[mid]) hi = mid - 1; else lo = mid + 1;\n        } else {\n            if (nums[mid] < target && target <= nums[hi]) lo = mid + 1; else hi = mid - 1;\n        }\n    }\n    return -1;\n}",
        "code_cpp": "int search(vector<int>& nums, int target) {\n    int lo = 0, hi = nums.size() - 1;\n    while (lo <= hi) {\n        int mid = (lo + hi) / 2;\n        if (nums[mid] == target) return mid;\n        if (nums[lo] <= nums[mid]) {\n            if (nums[lo] <= target && target < nums[mid]) hi = mid - 1; else lo = mid + 1;\n        } else {\n            if (nums[mid] < target && target <= nums[hi]) lo = mid + 1; else hi = mid - 1;\n        }\n    }\n    return -1;\n}",
        "code_c": "int search(int* nums, int n, int target) {\n    int lo = 0, hi = n - 1;\n    while (lo <= hi) {\n        int mid = (lo + hi) / 2;\n        if (nums[mid] == target) return mid;\n        if (nums[lo] <= nums[mid]) {\n            if (nums[lo] <= target && target < nums[mid]) hi = mid - 1; else lo = mid + 1;\n        } else {\n            if (nums[mid] < target && target <= nums[hi]) lo = mid + 1; else hi = mid - 1;\n        }\n    }\n    return -1;\n}",
    },
    ("Find Minimum in Rotated Sorted Array", "brute force"): {
        "code_java": "public int findMin(int[] nums) {\n    int min = nums[0];\n    for (int x : nums) if (x < min) min = x;\n    return min;\n}",
        "code_cpp": "int findMin(vector<int>& nums) {\n    int m = nums[0];\n    for (int x : nums) if (x < m) m = x;\n    return m;\n}",
        "code_c": "int findMin(int* nums, int n) {\n    int m = nums[0];\n    for (int i = 0; i < n; i++) if (nums[i] < m) m = nums[i];\n    return m;\n}",
    },
    ("Find Minimum in Rotated Sorted Array", "optimal (binary search)"): {
        "code_java": "public int findMin(int[] nums) {\n    int lo = 0, hi = nums.length - 1;\n    while (lo < hi) {\n        int mid = (lo + hi) / 2;\n        if (nums[mid] > nums[hi]) lo = mid + 1; else hi = mid;\n    }\n    return nums[lo];\n}",
        "code_cpp": "int findMin(vector<int>& nums) {\n    int lo = 0, hi = nums.size() - 1;\n    while (lo < hi) {\n        int mid = (lo + hi) / 2;\n        if (nums[mid] > nums[hi]) lo = mid + 1; else hi = mid;\n    }\n    return nums[lo];\n}",
        "code_c": "int findMin(int* nums, int n) {\n    int lo = 0, hi = n - 1;\n    while (lo < hi) {\n        int mid = (lo + hi) / 2;\n        if (nums[mid] > nums[hi]) lo = mid + 1; else hi = mid;\n    }\n    return nums[lo];\n}",
    },
    ("Longest Consecutive Sequence", "brute force (sort)"): {
        "code_java": "public int longestConsecutive(int[] nums) {\n    if (nums.length == 0) return 0;\n    Arrays.sort(nums);\n    int cur = 1, best = 1;\n    for (int i = 1; i < nums.length; i++) {\n        if (nums[i] == nums[i-1] + 1) cur++;\n        else if (nums[i] != nums[i-1]) cur = 1;\n        best = Math.max(best, cur);\n    }\n    return best;\n}",
        "code_cpp": "int longestConsecutive(vector<int>& nums) {\n    if (nums.empty()) return 0;\n    sort(nums.begin(), nums.end());\n    int cur = 1, best = 1;\n    for (int i = 1; i < (int)nums.size(); i++) {\n        if (nums[i] == nums[i-1] + 1) cur++;\n        else if (nums[i] != nums[i-1]) cur = 1;\n        best = max(best, cur);\n    }\n    return best;\n}",
        "code_c": "int cmp(const void* a, const void* b) { return *(int*)a - *(int*)b; }\nint longestConsecutive(int* nums, int n) {\n    if (n == 0) return 0;\n    qsort(nums, n, sizeof(int), cmp);\n    int cur = 1, best = 1;\n    for (int i = 1; i < n; i++) {\n        if (nums[i] == nums[i-1] + 1) cur++;\n        else if (nums[i] != nums[i-1]) cur = 1;\n        if (cur > best) best = cur;\n    }\n    return best;\n}",
    },
    ("Longest Consecutive Sequence", "optimal (hash set)"): {
        "code_java": "public int longestConsecutive(int[] nums) {\n    Set<Integer> set = new HashSet<>();\n    for (int x : nums) set.add(x);\n    int best = 0;\n    for (int x : set) {\n        if (!set.contains(x - 1)) {\n            int cur = 0, v = x;\n            while (set.contains(v)) { cur++; v++; }\n            best = Math.max(best, cur);\n        }\n    }\n    return best;\n}",
        "code_cpp": "int longestConsecutive(vector<int>& nums) {\n    unordered_set<int> st(nums.begin(), nums.end());\n    int best = 0;\n    for (int x : st) {\n        if (!st.count(x - 1)) {\n            int cur = 0, v = x;\n            while (st.count(v)) { cur++; v++; }\n            best = max(best, cur);\n        }\n    }\n    return best;\n}",
        "code_c": "int longestConsecutive(int* nums, int n) {\n    int min = nums[0], max = nums[0];\n    for (int i = 0; i < n; i++) { if (nums[i] < min) min = nums[i]; if (nums[i] > max) max = nums[i]; }\n    int range = max - min + 1;\n    int* seen = (int*)calloc(range, sizeof(int));\n    for (int i = 0; i < n; i++) seen[nums[i] - min] = 1;\n    int best = 0, cur = 0;\n    for (int i = 0; i < range; i++) {\n        if (seen[i]) cur++; else cur = 0;\n        if (cur > best) best = cur;\n    }\n    free(seen); return best;\n}",
    },
    ("Merge Intervals", "brute force"): {
        "code_java": "public int[][] merge(int[][] intervals) {\n    Arrays.sort(intervals, (a,b) -> a[0]-b[0]);\n    List<int[]> list = new ArrayList<>();\n    for (int[] x : intervals) list.add(x);\n    for (int i = 0; i < list.size(); i++)\n        for (int j = i + 1; j < list.size(); j++)\n            if (list.get(j)[0] <= list.get(i)[1]) {\n                list.get(i)[1] = Math.max(list.get(i)[1], list.get(j)[1]);\n                list.remove(j); j--;\n            }\n    return list.toArray(new int[0][]);\n}",
        "code_cpp": "vector<vector<int>> merge(vector<vector<int>>& intervals) {\n    sort(intervals.begin(), intervals.end());\n    for (int i = 0; i < (int)intervals.size(); i++)\n        for (int j = i + 1; j < (int)intervals.size(); j++)\n            if (intervals[j][0] <= intervals[i][1]) {\n                intervals[i][1] = max(intervals[i][1], intervals[j][1]);\n                intervals.erase(intervals.begin() + j); j--;\n            }\n    return intervals;\n}",
        "code_c": "int cmp(const void* a, const void* b) { return ((int*)a)[0] - ((int*)b)[0]; }\nint** merge(int** intervals, int n, int* colSizes, int* returnSize, int** returnColumnSizes) {\n    qsort(intervals, n, sizeof(int*), cmp);\n    for (int i = 0; i < n; i++)\n        for (int j = i + 1; j < n; j++)\n            if (intervals[j][0] <= intervals[i][1]) {\n                if (intervals[j][1] > intervals[i][1]) intervals[i][1] = intervals[j][1];\n                for (int k = j; k < n-1; k++) intervals[k] = intervals[k+1];\n                n--; j--;\n            }\n    *returnSize = n; *returnColumnSizes = colSizes; return intervals;\n}",
    },
    ("Merge Intervals", "optimal (sort + merge)"): {
        "code_java": "public int[][] merge(int[][] intervals) {\n    Arrays.sort(intervals, (a,b) -> a[0]-b[0]);\n    List<int[]> out = new ArrayList<>();\n    out.add(intervals[0]);\n    for (int i = 1; i < intervals.length; i++) {\n        if (intervals[i][0] <= out.get(out.size()-1)[1])\n            out.get(out.size()-1)[1] = Math.max(out.get(out.size()-1)[1], intervals[i][1]);\n        else out.add(intervals[i]);\n    }\n    return out.toArray(new int[0][]);\n}",
        "code_cpp": "vector<vector<int>> merge(vector<vector<int>>& intervals) {\n    sort(intervals.begin(), intervals.end());\n    vector<vector<int>> out = {intervals[0]};\n    for (int i = 1; i < (int)intervals.size(); i++) {\n        if (intervals[i][0] <= out.back()[1]) out.back()[1] = max(out.back()[1], intervals[i][1]);\n        else out.push_back(intervals[i]);\n    }\n    return out;\n}",
        "code_c": "int cmp(const void* a, const void* b) { return ((int*)a)[0] - ((int*)b)[0]; }\nint** merge(int** intervals, int n, int* colSizes, int* returnSize, int** returnColumnSizes) {\n    qsort(intervals, n, 2*sizeof(int), cmp);\n    int** out = (int**)malloc(n*sizeof(int*)); int sz = 0;\n    out[sz++] = intervals[0];\n    for (int i = 1; i < n; i++) {\n        if (intervals[i][0] <= out[sz-1][1]) { if (intervals[i][1] > out[sz-1][1]) out[sz-1][1] = intervals[i][1]; }\n        else out[sz++] = intervals[i];\n    }\n    *returnSize = sz; *returnColumnSizes = (int*)malloc(sz*sizeof(int)); for (int i=0;i<sz;i++) (*returnColumnSizes)[i]=2;\n    return out;\n}",
    },
    ("Jump Game", "brute force (dfs/dp)"): {
        "code_java": "public boolean canJump(int[] nums) {\n    return canJump(nums, 0);\n}\nboolean canJump(int[] nums, int i) {\n    if (i >= nums.length - 1) return true;\n    for (int j = 1; j <= nums[i]; j++) if (canJump(nums, i + j)) return true;\n    return false;\n}",
        "code_cpp": "bool canJump(vector<int>& nums, int i) {\n    if (i >= (int)nums.size() - 1) return true;\n    for (int j = 1; j <= nums[i]; j++) if (canJump(nums, i + j)) return true;\n    return false;\n}\nbool canJump(vector<int>& nums) { return canJump(nums, 0); }",
        "code_c": "int canJump(int* nums, int n, int i) {\n    if (i >= n - 1) return 1;\n    for (int j = 1; j <= nums[i] && i+j < n; j++) if (canJump(nums, n, i+j)) return 1;\n    return 0;\n}\nint canJump(int* nums, int n) { return n ? canJump(nums, n, 0) : 1; }",
    },
    ("Jump Game", "optimal (greedy)"): {
        "code_java": "public boolean canJump(int[] nums) {\n    int far = 0;\n    for (int i = 0; i < nums.length; i++) {\n        if (i > far) return false;\n        far = Math.max(far, i + nums[i]);\n    }\n    return true;\n}",
        "code_cpp": "bool canJump(vector<int>& nums) {\n    int far = 0;\n    for (int i = 0; i < (int)nums.size(); i++) {\n        if (i > far) return false;\n        far = max(far, i + nums[i]);\n    }\n    return true;\n}",
        "code_c": "int canJump(int* nums, int n) {\n    int far = 0;\n    for (int i = 0; i < n; i++) {\n        if (i > far) return 0;\n        if (i + nums[i] > far) far = i + nums[i];\n    }\n    return 1;\n}",
    },
    ("Jump Game II", "brute force (bfs)"): {
        "code_java": "public int jump(int[] nums) {\n    Queue<int[]> q = new LinkedList<>();\n    q.add(new int[]{0, 0});\n    Set<Integer> seen = new HashSet<>(); seen.add(0);\n    while (!q.isEmpty()) {\n        int[] cur = q.poll();\n        if (cur[0] >= nums.length - 1) return cur[1];\n        for (int j = cur[0] + 1; j < Math.min(cur[0] + nums[cur[0]] + 1, nums.length); j++)\n            if (seen.add(j)) q.add(new int[]{j, cur[1] + 1});\n    }\n    return -1;\n}",
        "code_cpp": "int jump(vector<int>& nums) {\n    queue<pair<int,int>> q; q.push({0,0});\n    set<int> seen; seen.insert(0);\n    while (!q.empty()) {\n        auto [i, steps] = q.front(); q.pop();\n        if (i >= (int)nums.size() - 1) return steps;\n        for (int j = i+1; j < min(i+nums[i]+1, (int)nums.size()); j++)\n            if (seen.insert(j).second) q.push({j, steps+1});\n    }\n    return -1;\n}",
        "code_c": "typedef struct { int i, steps; } node;\nint jump(int* nums, int n) {\n    node q[30000]; int front = 0, back = 0;\n    q[back++] = (node){0, 0};\n    int seen[30000] = {0}; seen[0] = 1;\n    while (front < back) {\n        node cur = q[front++];\n        if (cur.i >= n - 1) return cur.steps;\n        int end = cur.i + nums[cur.i] + 1; if (end > n) end = n;\n        for (int j = cur.i + 1; j < end; j++)\n            if (!seen[j]) { seen[j] = 1; q[back++] = (node){j, cur.steps + 1}; }\n    }\n    return -1;\n}",
    },
    ("Jump Game II", "optimal (greedy)"): {
        "code_java": "public int jump(int[] nums) {\n    int jumps = 0, end = 0, far = 0;\n    for (int i = 0; i < nums.length - 1; i++) {\n        far = Math.max(far, i + nums[i]);\n        if (i == end) { jumps++; end = far; }\n    }\n    return jumps;\n}",
        "code_cpp": "int jump(vector<int>& nums) {\n    int jumps = 0, end = 0, far = 0;\n    for (int i = 0; i < (int)nums.size() - 1; i++) {\n        far = max(far, i + nums[i]);\n        if (i == end) { jumps++; end = far; }\n    }\n    return jumps;\n}",
        "code_c": "int jump(int* nums, int n) {\n    if (n <= 1) return 0;\n    int jumps = 0, end = 0, far = 0;\n    for (int i = 0; i < n - 1; i++) {\n        if (i + nums[i] > far) far = i + nums[i];\n        if (i == end) { jumps++; end = far; }\n    }\n    return jumps;\n}",
    },
    ("Unique Paths", "brute force (recursion)"): {
        "code_java": "public int uniquePaths(int m, int n) {\n    if (m == 1 || n == 1) return 1;\n    return uniquePaths(m-1, n) + uniquePaths(m, n-1);\n}",
        "code_cpp": "int uniquePaths(int m, int n) {\n    if (m == 1 || n == 1) return 1;\n    return uniquePaths(m-1, n) + uniquePaths(m, n-1);\n}",
        "code_c": "int uniquePaths(int m, int n) {\n    if (m == 1 || n == 1) return 1;\n    return uniquePaths(m-1, n) + uniquePaths(m, n-1);\n}",
    },
    ("Unique Paths", "optimal (dp / math)"): {
        "code_java": "public int uniquePaths(int m, int n) {\n    int[] dp = new int[n];\n    Arrays.fill(dp, 1);\n    for (int i = 1; i < m; i++)\n        for (int j = 1; j < n; j++) dp[j] += dp[j-1];\n    return dp[n-1];\n}",
        "code_cpp": "int uniquePaths(int m, int n) {\n    vector<int> dp(n, 1);\n    for (int i = 1; i < m; i++)\n        for (int j = 1; j < n; j++) dp[j] += dp[j-1];\n    return dp[n-1];\n}",
        "code_c": "int uniquePaths(int m, int n) {\n    int* dp = (int*)malloc(n*sizeof(int));\n    for (int j = 0; j < n; j++) dp[j] = 1;\n    for (int i = 1; i < m; i++)\n        for (int j = 1; j < n; j++) dp[j] += dp[j-1];\n    int r = dp[n-1]; free(dp); return r;\n}",
    },
    ("Minimum Path Sum", "brute force (recursion)"): {
        "code_java": "public int minPathSum(int[][] grid) {\n    return minPathSum(grid, 0, 0);\n}\nint minPathSum(int[][] grid, int r, int c) {\n    if (r >= grid.length || c >= grid[0].length) return Integer.MAX_VALUE;\n    if (r == grid.length-1 && c == grid[0].length-1) return grid[r][c];\n    return grid[r][c] + Math.min(minPathSum(grid, r+1, c), minPathSum(grid, r, c+1));\n}",
        "code_cpp": "int minPathSum(vector<vector<int>>& grid, int r, int c) {\n    if (r >= (int)grid.size() || c >= (int)grid[0].size()) return INT_MAX;\n    if (r == grid.size()-1 && c == grid[0].size()-1) return grid[r][c];\n    return grid[r][c] + min(minPathSum(grid, r+1, c), minPathSum(grid, r, c+1));\n}\nint minPathSum(vector<vector<int>>& grid) { return minPathSum(grid, 0, 0); }",
        "code_c": "int minPathSum(int** grid, int m, int n, int r, int c) {\n    if (r >= m || c >= n) return 2147483647;\n    if (r == m-1 && c == n-1) return grid[r][c];\n    int a = minPathSum(grid, m, n, r+1, c), b = minPathSum(grid, m, n, r, c+1);\n    return grid[r][c] + (a < b ? a : b);\n}\nint minPathSum(int** grid, int m, int n) { return minPathSum(grid, m, n, 0, 0); }",
    },
    ("Minimum Path Sum", "optimal (dp)"): {
        "code_java": "public int minPathSum(int[][] grid) {\n    int m = grid.length, n = grid[0].length;\n    for (int j = n-2; j >= 0; j--) grid[m-1][j] += grid[m-1][j+1];\n    for (int i = m-2; i >= 0; i--) {\n        grid[i][n-1] += grid[i+1][n-1];\n        for (int j = n-2; j >= 0; j--) grid[i][j] += Math.min(grid[i+1][j], grid[i][j+1]);\n    }\n    return grid[0][0];\n}",
        "code_cpp": "int minPathSum(vector<vector<int>>& grid) {\n    int m = grid.size(), n = grid[0].size();\n    for (int j = n-2; j >= 0; j--) grid[m-1][j] += grid[m-1][j+1];\n    for (int i = m-2; i >= 0; i--) {\n        grid[i][n-1] += grid[i+1][n-1];\n        for (int j = n-2; j >= 0; j--) grid[i][j] += min(grid[i+1][j], grid[i][j+1]);\n    }\n    return grid[0][0];\n}",
        "code_c": "int minPathSum(int** grid, int m, int n) {\n    for (int j = n-2; j >= 0; j--) grid[m-1][j] += grid[m-1][j+1];\n    for (int i = m-2; i >= 0; i--) {\n        grid[i][n-1] += grid[i+1][n-1];\n        for (int j = n-2; j >= 0; j--) grid[i][j] += (grid[i+1][j] < grid[i][j+1] ? grid[i+1][j] : grid[i][j+1]);\n    }\n    return grid[0][0];\n}",
    },
    ("Reverse String", "brute force"): {
        "code_java": "public void reverseString(char[] s) {\n    for (int i = 0, j = s.length - 1; i < j; i++, j--) {\n        char t = s[i]; s[i] = s[j]; s[j] = t;\n    }\n}",
        "code_cpp": "void reverseString(vector<char>& s) {\n    for (int i = 0, j = s.size() - 1; i < j; i++, j--) swap(s[i], s[j]);\n}",
        "code_c": "void reverseString(char* s, int n) {\n    for (int i = 0, j = n - 1; i < j; i++, j--) { char t = s[i]; s[i] = s[j]; s[j] = t; }\n}",
    },
    ("Reverse String", "optimal (two pointers)"): {
        "code_java": "public void reverseString(char[] s) {\n    int l = 0, r = s.length - 1;\n    while (l < r) { char t = s[l]; s[l++] = s[r]; s[r--] = t; }\n}",
        "code_cpp": "void reverseString(vector<char>& s) {\n    int l = 0, r = s.size() - 1;\n    while (l < r) swap(s[l++], s[r--]);\n}",
        "code_c": "void reverseString(char* s, int n) {\n    int l = 0, r = n - 1;\n    while (l < r) { char t = s[l]; s[l++] = s[r]; s[r--] = t; }\n}",
    },
    ("Valid Parentheses", "brute force"): {
        "code_java": "public boolean isValid(String s) {\n    while (s.contains(\"()\") || s.contains(\"[]\") || s.contains(\"{}\"))\n        s = s.replace(\"()\",\"\").replace(\"[]\",\"\").replace(\"{}\",\"\");\n    return s.isEmpty();\n}",
        "code_cpp": "bool isValid(string s) {\n    size_t n;\n    while ((n = s.size()) && (s.find(\"()\") != string::npos || s.find(\"[]\") != string::npos || s.find(\"{}\") != string::npos))\n        s.erase(s.find(\"()\") != string::npos ? s.find(\"()\") : s.find(\"[]\") != string::npos ? s.find(\"[]\") : s.find(\"{}\"), 2);\n    return s.empty();\n}",
        "code_c": "int isValid(char* s) {\n    char st[10000]; int top = 0;\n    for (; *s; s++) {\n        if (*s == '(' || *s == '[' || *s == '{') st[top++] = *s;\n        else if (top == 0) return 0;\n        else if (*s == ')' && st[top-1] != '(') return 0;\n        else if (*s == ']' && st[top-1] != '[') return 0;\n        else if (*s == '}' && st[top-1] != '{') return 0;\n        else top--;\n    }\n    return top == 0;\n}",
    },
    ("Valid Parentheses", "optimal (stack)"): {
        "code_java": "public boolean isValid(String s) {\n    Stack<Character> st = new Stack<>();\n    for (char c : s.toCharArray()) {\n        if (c == '(' || c == '[' || c == '{') st.push(c);\n        else if (st.isEmpty() || (c == ')' && st.pop() != '(') || (c == ']' && st.pop() != '[') || (c == '}' && st.pop() != '{')) return false;\n    }\n    return st.isEmpty();\n}",
        "code_cpp": "bool isValid(string s) {\n    stack<char> st;\n    for (char c : s) {\n        if (c == '(' || c == '[' || c == '{') st.push(c);\n        else if (st.empty() || (c == ')' && st.top() != '(') || (c == ']' && st.top() != '[') || (c == '}' && st.top() != '{')) return false;\n        else st.pop();\n    }\n    return st.empty();\n}",
        "code_c": "int isValid(char* s) {\n    char st[10000]; int top = 0;\n    for (; *s; s++) {\n        if (*s == '(' || *s == '[' || *s == '{') st[top++] = *s;\n        else if (top == 0) return 0;\n        else if (*s == ')' && st[top-1] != '(') return 0;\n        else if (*s == ']' && st[top-1] != '[') return 0;\n        else if (*s == '}' && st[top-1] != '{') return 0;\n        else top--;\n    }\n    return top == 0;\n}",
    },
    ("Merge Two Sorted Lists", "brute force"): {
        "code_java": "public ListNode mergeTwoLists(ListNode l1, ListNode l2) {\n    List<Integer> vals = new ArrayList<>();\n    while (l1 != null) { vals.add(l1.val); l1 = l1.next; }\n    while (l2 != null) { vals.add(l2.val); l2 = l2.next; }\n    Collections.sort(vals);\n    ListNode dummy = new ListNode(0), p = dummy;\n    for (int v : vals) { p.next = new ListNode(v); p = p.next; }\n    return dummy.next;\n}",
        "code_cpp": "ListNode* mergeTwoLists(ListNode* l1, ListNode* l2) {\n    vector<int> vals;\n    while (l1) { vals.push_back(l1->val); l1 = l1->next; }\n    while (l2) { vals.push_back(l2->val); l2 = l2->next; }\n    sort(vals.begin(), vals.end());\n    ListNode dummy(0); ListNode* p = &dummy;\n    for (int v : vals) { p->next = new ListNode(v); p = p->next; }\n    return dummy.next;\n}",
        "code_c": "int cmp(const void* a, const void* b) { return *(int*)a - *(int*)b; }\nstruct ListNode* mergeTwoLists(struct ListNode* l1, struct ListNode* l2) {\n    int arr[200]; int n = 0;\n    while (l1) { arr[n++] = l1->val; l1 = l1->next; }\n    while (l2) { arr[n++] = l2->val; l2 = l2->next; }\n    qsort(arr, n, sizeof(int), cmp);\n    struct ListNode dummy = {0, NULL}, *p = &dummy;\n    for (int i = 0; i < n; i++) { p->next = (struct ListNode*)malloc(sizeof(struct ListNode)); p->next->val = arr[i]; p->next->next = NULL; p = p->next; }\n    return dummy.next;\n}",
    },
    ("Merge Two Sorted Lists", "optimal (two pointers)"): {
        "code_java": "public ListNode mergeTwoLists(ListNode l1, ListNode l2) {\n    ListNode dummy = new ListNode(0), p = dummy;\n    while (l1 != null && l2 != null) {\n        if (l1.val <= l2.val) { p.next = l1; l1 = l1.next; } else { p.next = l2; l2 = l2.next; }\n        p = p.next;\n    }\n    p.next = l1 != null ? l1 : l2;\n    return dummy.next;\n}",
        "code_cpp": "ListNode* mergeTwoLists(ListNode* l1, ListNode* l2) {\n    ListNode dummy(0); ListNode* p = &dummy;\n    while (l1 && l2) {\n        if (l1->val <= l2->val) { p->next = l1; l1 = l1->next; } else { p->next = l2; l2 = l2->next; }\n        p = p->next;\n    }\n    p->next = l1 ? l1 : l2;\n    return dummy.next;\n}",
        "code_c": "struct ListNode* mergeTwoLists(struct ListNode* l1, struct ListNode* l2) {\n    struct ListNode dummy = {0, NULL}, *p = &dummy;\n    while (l1 && l2) {\n        if (l1->val <= l2->val) { p->next = l1; l1 = l1->next; } else { p->next = l2; l2 = l2->next; }\n        p = p->next;\n    }\n    p->next = l1 ? l1 : l2;\n    return dummy.next;\n}",
    },
    ("Subsets", "brute force (iterative)"): {
        "code_java": "public List<List<Integer>> subsets(int[] nums) {\n    List<List<Integer>> res = new ArrayList<>();\n    res.add(new ArrayList<>());\n    for (int x : nums) {\n        int sz = res.size();\n        for (int i = 0; i < sz; i++) {\n            List<Integer> copy = new ArrayList<>(res.get(i));\n            copy.add(x);\n            res.add(copy);\n        }\n    }\n    return res;\n}",
        "code_cpp": "vector<vector<int>> subsets(vector<int>& nums) {\n    vector<vector<int>> res = {{}};\n    for (int x : nums) {\n        int sz = res.size();\n        for (int i = 0; i < sz; i++) { res.push_back(res[i]); res.back().push_back(x); }\n    }\n    return res;\n}",
        "code_c": "int** subsets(int* nums, int n, int* returnSize, int** returnColumnSizes) {\n    int cap = 1 << n;\n    int** res = (int**)malloc(cap*sizeof(int*));\n    *returnColumnSizes = (int*)malloc(cap*sizeof(int));\n    res[0] = NULL; (*returnColumnSizes)[0] = 0; *returnSize = 1;\n    for (int i = 0; i < n; i++) {\n        int sz = *returnSize;\n        for (int j = 0; j < sz; j++) {\n            int len = (*returnColumnSizes)[j];\n            res[*returnSize] = (int*)malloc((len+1)*sizeof(int));\n            for (int k = 0; k < len; k++) res[*returnSize][k] = res[j][k];\n            res[*returnSize][len] = nums[i];\n            (*returnColumnSizes)[*returnSize] = len + 1;\n            (*returnSize)++;\n        }\n    }\n    return res;\n}",
    },
    ("Subsets", "optimal (backtracking)"): {
        "code_java": "List<List<Integer>> res;\nvoid bt(int[] nums, int i, List<Integer> path) {\n    res.add(new ArrayList<>(path));\n    for (int j = i; j < nums.length; j++) {\n        path.add(nums[j]); bt(nums, j+1, path); path.remove(path.size()-1);\n    }\n}\npublic List<List<Integer>> subsets(int[] nums) {\n    res = new ArrayList<>(); bt(nums, 0, new ArrayList<>()); return res;\n}",
        "code_cpp": "vector<vector<int>> res;\nvoid bt(vector<int>& nums, int i, vector<int>& path) {\n    res.push_back(path);\n    for (int j = i; j < (int)nums.size(); j++) {\n        path.push_back(nums[j]); bt(nums, j+1, path); path.pop_back();\n    }\n}\nvector<vector<int>> subsets(vector<int>& nums) { res.clear(); vector<int> path; bt(nums, 0, path); return res; }",
        "code_c": "void bt(int* nums, int n, int i, int* path, int len, int** res, int* colSizes, int* sz) {\n    res[*sz] = (int*)malloc(len*sizeof(int));\n    for (int k = 0; k < len; k++) res[*sz][k] = path[k];\n    colSizes[(*sz)++] = len;\n    for (int j = i; j < n; j++) { path[len] = nums[j]; bt(nums, n, j+1, path, len+1, res, colSizes, sz); }\n}\nint** subsets(int* nums, int n, int* returnSize, int** returnColumnSizes) {\n    int cap = 1<<n; int** res = (int**)malloc(cap*sizeof(int*)); *returnColumnSizes = (int*)malloc(cap*sizeof(int));\n    int* path = (int*)malloc(n*sizeof(int)); *returnSize = 0;\n    bt(nums, n, 0, path, 0, res, *returnColumnSizes, returnSize);\n    return res;\n}",
    },
    ("Target Sum", "brute force (recursion)"): {
        "code_java": "public int findTargetSumWays(int[] nums, int target) {\n    return f(nums, 0, 0, target);\n}\nint f(int[] nums, int i, int sum, int target) {\n    if (i == nums.length) return sum == target ? 1 : 0;\n    return f(nums, i+1, sum+nums[i], target) + f(nums, i+1, sum-nums[i], target);\n}",
        "code_cpp": "int f(vector<int>& nums, int i, int sum, int target) {\n    if (i == (int)nums.size()) return sum == target ? 1 : 0;\n    return f(nums, i+1, sum+nums[i], target) + f(nums, i+1, sum-nums[i], target);\n}\nint findTargetSumWays(vector<int>& nums, int target) { return f(nums, 0, 0, target); }",
        "code_c": "int f(int* nums, int n, int i, int sum, int target) {\n    if (i == n) return sum == target ? 1 : 0;\n    return f(nums, n, i+1, sum+nums[i], target) + f(nums, n, i+1, sum-nums[i], target);\n}\nint findTargetSumWays(int* nums, int n, int target) { return f(nums, n, 0, 0, target); }",
    },
    ("Target Sum", "optimal (dp / subset sum)"): {
        "code_java": "public int findTargetSumWays(int[] nums, int target) {\n    int total = 0;\n    for (int x : nums) total += x;\n    if ((total + target) % 2 != 0 || total + target < 0) return 0;\n    int t = (total + target) / 2;\n    int[] dp = new int[t+1]; dp[0] = 1;\n    for (int x : nums)\n        for (int j = t; j >= x; j--) dp[j] += dp[j-x];\n    return dp[t];\n}",
        "code_cpp": "int findTargetSumWays(vector<int>& nums, int target) {\n    int total = 0;\n    for (int x : nums) total += x;\n    if ((total + target) % 2 != 0 || total + target < 0) return 0;\n    int t = (total + target) / 2;\n    vector<int> dp(t+1, 0); dp[0] = 1;\n    for (int x : nums)\n        for (int j = t; j >= x; j--) dp[j] += dp[j-x];\n    return dp[t];\n}",
        "code_c": "int findTargetSumWays(int* nums, int n, int target) {\n    int total = 0;\n    for (int i = 0; i < n; i++) total += nums[i];\n    if ((total + target) % 2 != 0 || total + target < 0) return 0;\n    int t = (total + target) / 2;\n    int* dp = (int*)calloc(t+1, sizeof(int)); dp[0] = 1;\n    for (int i = 0; i < n; i++)\n        for (int j = t; j >= nums[i]; j--) dp[j] += dp[j-nums[i]];\n    int r = dp[t]; free(dp); return r;\n}",
    },
    ("Top K Frequent Elements", "brute force (sort by freq)"): {
        "code_java": "public int[] topKFrequent(int[] nums, int k) {\n    Map<Integer, Integer> map = new HashMap<>();\n    for (int x : nums) map.put(x, map.getOrDefault(x, 0) + 1);\n    return map.entrySet().stream().sorted((a,b)->b.getValue()-a.getValue()).limit(k).mapToInt(e->e.getKey()).toArray();\n}",
        "code_cpp": "vector<int> topKFrequent(vector<int>& nums, int k) {\n    unordered_map<int, int> m;\n    for (int x : nums) m[x]++;\n    vector<pair<int,int>> v(m.begin(), m.end());\n    sort(v.begin(), v.end(), [](auto& a, auto& b) { return a.second > b.second; });\n    vector<int> res;\n    for (int i = 0; i < k; i++) res.push_back(v[i].first);\n    return res;\n}",
        "code_c": "typedef struct { int val, cnt; } pair;\nint cmp(const void* a, const void* b) { return ((pair*)b)->cnt - ((pair*)a)->cnt; }\nint* topKFrequent(int* nums, int n, int k, int* returnSize) {\n    int cnt[20001] = {0}, uniq[20001], u = 0;\n    for (int i = 0; i < n; i++) { int x = nums[i] + 10000; if (!cnt[x]) uniq[u++] = x; cnt[x]++; }\n    pair* arr = (pair*)malloc(u*sizeof(pair));\n    for (int i = 0; i < u; i++) { arr[i].val = uniq[i] - 10000; arr[i].cnt = cnt[uniq[i]]; }\n    qsort(arr, u, sizeof(pair), cmp);\n    int* res = (int*)malloc(k*sizeof(int));\n    for (int i = 0; i < k; i++) res[i] = arr[i].val;\n    *returnSize = k; return res;\n}",
    },
    ("Top K Frequent Elements", "optimal (bucket sort)"): {
        "code_java": "public int[] topKFrequent(int[] nums, int k) {\n    Map<Integer, Integer> map = new HashMap<>();\n    for (int x : nums) map.put(x, map.getOrDefault(x, 0) + 1);\n    List<Integer>[] buckets = new List[nums.length + 1];\n    for (int i = 0; i <= nums.length; i++) buckets[i] = new ArrayList<>();\n    for (Map.Entry<Integer, Integer> e : map.entrySet()) buckets[e.getValue()].add(e.getKey());\n    int[] res = new int[k]; int idx = 0;\n    for (int i = nums.length; i >= 0 && idx < k; i--)\n        for (int x : buckets[i]) { res[idx++] = x; if (idx == k) break; }\n    return res;\n}",
        "code_cpp": "vector<int> topKFrequent(vector<int>& nums, int k) {\n    unordered_map<int, int> m;\n    for (int x : nums) m[x]++;\n    vector<vector<int>> buckets(nums.size() + 1);\n    for (auto& p : m) buckets[p.second].push_back(p.first);\n    vector<int> res;\n    for (int i = nums.size(); i >= 0 && (int)res.size() < k; i--)\n        for (int x : buckets[i]) { res.push_back(x); if ((int)res.size() == k) break; }\n    return res;\n}",
        "code_c": "int* topKFrequent(int* nums, int n, int k, int* returnSize) {\n    int cnt[20001] = {0}, uniq[20001], u = 0;\n    for (int i = 0; i < n; i++) { int x = nums[i] + 10000; if (!cnt[x]) uniq[u++] = x; cnt[x]++; }\n    int** buckets = (int**)calloc(n+1, sizeof(int*)); int* bsz = (int*)calloc(n+1, sizeof(int));\n    for (int i = 0; i < u; i++) { int c = cnt[uniq[i]]; buckets[c] = (int*)realloc(buckets[c], (bsz[c]+1)*sizeof(int)); buckets[c][bsz[c]++] = uniq[i]-10000; }\n    int* res = (int*)malloc(k*sizeof(int)); int idx = 0;\n    for (int i = n; i >= 0 && idx < k; i--) for (int j = 0; j < bsz[i] && idx < k; j++) res[idx++] = buckets[i][j];\n    *returnSize = k; return res;\n}",
    },
    ("Two Sum II - Input Array Is Sorted", "brute force"): {
        "code_java": "public int[] twoSum(int[] numbers, int target) {\n    for (int i = 0; i < numbers.length; i++)\n        for (int j = i + 1; j < numbers.length; j++)\n            if (numbers[i] + numbers[j] == target) return new int[]{i+1, j+1};\n    return new int[]{};\n}",
        "code_cpp": "vector<int> twoSum(vector<int>& numbers, int target) {\n    for (int i = 0; i < (int)numbers.size(); i++)\n        for (int j = i + 1; j < (int)numbers.size(); j++)\n            if (numbers[i] + numbers[j] == target) return {i+1, j+1};\n    return {};\n}",
        "code_c": "int* twoSum(int* numbers, int n, int target, int* returnSize) {\n    *returnSize = 2;\n    int* out = (int*)malloc(2*sizeof(int));\n    for (int i = 0; i < n; i++)\n        for (int j = i + 1; j < n; j++)\n            if (numbers[i] + numbers[j] == target) { out[0] = i+1; out[1] = j+1; return out; }\n    return out;\n}",
    },
    ("Two Sum II - Input Array Is Sorted", "optimal (two pointers)"): {
        "code_java": "public int[] twoSum(int[] numbers, int target) {\n    int l = 0, r = numbers.length - 1;\n    while (l < r) {\n        int s = numbers[l] + numbers[r];\n        if (s == target) return new int[]{l+1, r+1};\n        if (s < target) l++; else r--;\n    }\n    return new int[]{};\n}",
        "code_cpp": "vector<int> twoSum(vector<int>& numbers, int target) {\n    int l = 0, r = numbers.size() - 1;\n    while (l < r) {\n        int s = numbers[l] + numbers[r];\n        if (s == target) return {l+1, r+1};\n        if (s < target) l++; else r--;\n    }\n    return {};\n}",
        "code_c": "int* twoSum(int* numbers, int n, int target, int* returnSize) {\n    *returnSize = 2;\n    int* out = (int*)malloc(2*sizeof(int));\n    int l = 0, r = n - 1;\n    while (l < r) {\n        int s = numbers[l] + numbers[r];\n        if (s == target) { out[0] = l+1; out[1] = r+1; return out; }\n        if (s < target) l++; else r--;\n    }\n    return out;\n}",
    },
    ("Trapping Rain Water", "brute force"): {
        "code_java": "public int trap(int[] height) {\n    int n = height.length;\n    int[] left = new int[n], right = new int[n];\n    left[0] = height[0]; for (int i = 1; i < n; i++) left[i] = Math.max(left[i-1], height[i]);\n    right[n-1] = height[n-1]; for (int i = n-2; i >= 0; i--) right[i] = Math.max(right[i+1], height[i]);\n    int sum = 0;\n    for (int i = 0; i < n; i++) sum += Math.min(left[i], right[i]) - height[i];\n    return sum;\n}",
        "code_cpp": "int trap(vector<int>& height) {\n    int n = height.size();\n    vector<int> left(n), right(n);\n    left[0] = height[0]; for (int i = 1; i < n; i++) left[i] = max(left[i-1], height[i]);\n    right[n-1] = height[n-1]; for (int i = n-2; i >= 0; i--) right[i] = max(right[i+1], height[i]);\n    int sum = 0;\n    for (int i = 0; i < n; i++) sum += min(left[i], right[i]) - height[i];\n    return sum;\n}",
        "code_c": "int trap(int* height, int n) {\n    if (n == 0) return 0;\n    int* left = (int*)malloc(n*sizeof(int));\n    int* right = (int*)malloc(n*sizeof(int));\n    left[0] = height[0]; for (int i = 1; i < n; i++) left[i] = (height[i] > left[i-1]) ? height[i] : left[i-1];\n    right[n-1] = height[n-1]; for (int i = n-2; i >= 0; i--) right[i] = (height[i] > right[i+1]) ? height[i] : right[i+1];\n    int sum = 0;\n    for (int i = 0; i < n; i++) sum += (left[i] < right[i] ? left[i] : right[i]) - height[i];\n    free(left); free(right); return sum;\n}",
    },
    ("Trapping Rain Water", "optimal (two pointers)"): {
        "code_java": "public int trap(int[] height) {\n    int l = 0, r = height.length - 1, maxL = 0, maxR = 0, total = 0;\n    while (l < r) {\n        if (height[l] <= height[r]) {\n            maxL = Math.max(maxL, height[l]); total += maxL - height[l]; l++;\n        } else {\n            maxR = Math.max(maxR, height[r]); total += maxR - height[r]; r--;\n        }\n    }\n    return total;\n}",
        "code_cpp": "int trap(vector<int>& height) {\n    int l = 0, r = height.size() - 1, maxL = 0, maxR = 0, total = 0;\n    while (l < r) {\n        if (height[l] <= height[r]) { maxL = max(maxL, height[l]); total += maxL - height[l]; l++; }\n        else { maxR = max(maxR, height[r]); total += maxR - height[r]; r--; }\n    }\n    return total;\n}",
        "code_c": "int trap(int* height, int n) {\n    int l = 0, r = n - 1, maxL = 0, maxR = 0, total = 0;\n    while (l < r) {\n        if (height[l] <= height[r]) { if (height[l] > maxL) maxL = height[l]; total += maxL - height[l]; l++; }\n        else { if (height[r] > maxR) maxR = height[r]; total += maxR - height[r]; r--; }\n    }\n    return total;\n}",
    },
}

try:
    from solution_code_multilang_extra import MULTILANG_EXTRA
    MULTILANG.update(MULTILANG_EXTRA)
except ImportError:
    pass

def get_multilang(problem_title: str, approach_title: str) -> dict:
    """Return dict with code_java, code_cpp, code_c for this problem/approach (real code only)."""
    k = _key(problem_title, approach_title)
    return dict(MULTILANG.get(k, {}))
