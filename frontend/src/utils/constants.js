export const DIFFICULTY_COLORS = {
  easy: 'text-green-400',
  medium: 'text-yellow-400',
  hard: 'text-red-400',
};

export const DIFFICULTY_BG = {
  easy: 'bg-green-500/10 border-green-500/20',
  medium: 'bg-yellow-500/10 border-yellow-500/20',
  hard: 'bg-red-500/10 border-red-500/20',
};

export const STATUS_COLORS = {
  accepted: 'text-green-400',
  wrong_answer: 'text-red-400',
  time_limit_exceeded: 'text-yellow-400',
  runtime_error: 'text-orange-400',
  compile_error: 'text-red-400',
};

export const STARTER_CODE = {
  python: {
    twoSum: `def twoSum(nums, target):
    # Write your code here
    pass

if __name__ == "__main__":
    import sys
    input_data = sys.stdin.read().strip().split('\\n')
    nums = list(map(int, input_data[0].split()))
    target = int(input_data[1])
    result = twoSum(nums, target)
    print(' '.join(map(str, result)))`,
  },
  javascript: {
    twoSum: `function twoSum(nums, target) {
    // Write your code here
}

const readline = require('readline');
const rl = readline.createInterface({
    input: process.stdin
});

const lines = [];
rl.on('line', (line) => lines.push(line));
rl.on('close', () => {
    const nums = lines[0].split(' ').map(Number);
    const target = parseInt(lines[1]);
    const result = twoSum(nums, target);
    console.log(result.join(' '));
});`,
  },
};
