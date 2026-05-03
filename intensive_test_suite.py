#!/usr/bin/env python3
"""
INTENSIVE TEST SUITE FOR 0/1 KNAPSACK ALGORITHMS
==============================================
Tests all 5 algorithms against hundreds of benchmark instances
Verifies correctness, consistency, and performance metrics
"""

import os
import sys
import time
import csv
from pathlib import Path

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.algorithms.brute_force import knapsack_brute_force
from src.algorithms.memoization import knapsack_memoization
from src.algorithms.tabulation import knapsack_tabulation
from src.algorithms.space_optimised import knapsack_space_optimised
from src.algorithms.greedy import knapsack_greedy
from src.parse_kp import parse_kp


class TestSuite:
    def __init__(self):
        self.results = []
        self.kplib_root = 'testcases/kplib'
        self.test_categories = []
        self.total_tests = 0
        self.passed_tests = 0
        self.failed_tests = 0
        
    def find_test_instances(self, max_per_size=5):
        """Find all available test instances from kplib"""
        instances = []
        
        for category_dir in sorted(Path(self.kplib_root).iterdir()):
            if not category_dir.is_dir():
                continue
            
            category = category_dir.name
            
            for size_dir in sorted(category_dir.iterdir()):
                if not size_dir.is_dir():
                    continue
                
                size_label = size_dir.name  # e.g., n00050
                
                for ratio_dir in sorted(size_dir.iterdir()):
                    if not ratio_dir.is_dir():
                        continue
                    
                    ratio = ratio_dir.name  # e.g., R01000
                    
                    # Get kp files
                    kp_files = list(ratio_dir.glob('*.kp'))[:max_per_size]
                    
                    for kp_file in kp_files:
                        instances.append({
                            'path': str(kp_file),
                            'category': category,
                            'size': size_label,
                            'ratio': ratio,
                            'filename': kp_file.name
                        })
        
        return instances
    
    def test_single_instance(self, instance):
        """Test all algorithms on a single instance"""
        try:
            n, capacity, values, weights = parse_kp(instance['path'])
        except Exception as e:
            return {
                'instance': instance['filename'],
                'category': instance['category'],
                'size': instance['size'],
                'n': -1,
                'capacity': -1,
                'status': 'PARSE_ERROR',
                'error': str(e)
            }
        
        instance['n'] = n
        instance['capacity'] = capacity
        
        result = {
            'instance': instance['filename'],
            'category': instance['category'],
            'size': instance['size'],
            'ratio': instance['ratio'],
            'n': n,
            'capacity': capacity,
            'algorithms': {}
        }
        
        # Test Brute Force (skip if too large)
        bf_result = None
        bf_time = None
        bf_skipped = False
        if n <= 20:
            try:
                start = time.perf_counter()
                bf_result = knapsack_brute_force(capacity, n, values, weights)
                bf_time = (time.perf_counter() - start) * 1000
            except Exception as e:
                bf_result = f"ERROR: {str(e)[:50]}"
        else:
            bf_skipped = True
        
        result['algorithms']['BruteForce'] = {
            'result': bf_result,
            'time_ms': bf_time,
            'skipped': bf_skipped
        }
        
        # Test Memoization (skip if too large)
        memo_result = None
        memo_time = None
        memo_skipped = False
        if n * capacity <= 5_000_000:  # Memory safety
            try:
                memo = [[None] * (capacity + 1) for _ in range(n + 1)]
                start = time.perf_counter()
                memo_result = knapsack_memoization(capacity, n, values, weights, memo)
                memo_time = (time.perf_counter() - start) * 1000
            except Exception as e:
                memo_result = f"ERROR: {str(e)[:50]}"
        else:
            memo_skipped = True
        
        result['algorithms']['Memoization'] = {
            'result': memo_result,
            'time_ms': memo_time,
            'skipped': memo_skipped
        }
        
        # Test Tabulation (main reference algorithm)
        tab_result = None
        tab_time = None
        tab_items = None
        tab_skipped = False
        if n * capacity <= 10_000_000:  # Memory safety
            try:
                start = time.perf_counter()
                tab_result, tab_items = knapsack_tabulation(capacity, values, weights)
                tab_time = (time.perf_counter() - start) * 1000
            except Exception as e:
                tab_result = f"ERROR: {str(e)[:50]}"
        else:
            tab_skipped = True
        
        result['algorithms']['Tabulation'] = {
            'result': tab_result,
            'time_ms': tab_time,
            'items': len(tab_items) if tab_items else 0,
            'skipped': tab_skipped
        }
        
        # Test Space-Optimised
        so_result = None
        so_time = None
        so_skipped = False
        if n * capacity <= 20_000_000:
            try:
                start = time.perf_counter()
                so_result = knapsack_space_optimised(values, weights, n, capacity)
                so_time = (time.perf_counter() - start) * 1000
            except Exception as e:
                so_result = f"ERROR: {str(e)[:50]}"
        else:
            so_skipped = True
        
        result['algorithms']['SpaceOptimised'] = {
            'result': so_result,
            'time_ms': so_time,
            'skipped': so_skipped
        }
        
        # Test Greedy (always runs)
        greedy_result = None
        greedy_time = None
        try:
            start = time.perf_counter()
            greedy_result = knapsack_greedy(capacity, values, weights)
            greedy_time = (time.perf_counter() - start) * 1000
        except Exception as e:
            greedy_result = f"ERROR: {str(e)[:50]}"
        
        result['algorithms']['Greedy'] = {
            'result': greedy_result,
            'time_ms': greedy_time,
            'skipped': False
        }
        
        # Verify consistency
        result['verification'] = self._verify_results(result)
        
        return result
    
    def _verify_results(self, result):
        """Verify that results are consistent across algorithms"""
        verification = {
            'all_exact_match': False,
            'optimal_found': False,
            'greedy_consistent': False,
            'notes': []
        }
        
        algs = result['algorithms']
        exact_results = []
        
        # Collect exact algorithm results (non-skipped, non-error)
        for alg_name in ['BruteForce', 'Memoization', 'Tabulation', 'SpaceOptimised']:
            alg_data = algs[alg_name]
            if not alg_data['skipped'] and isinstance(alg_data['result'], int):
                exact_results.append((alg_name, alg_data['result']))
        
        # Check if all exact algorithms agree
        if exact_results:
            first_result = exact_results[0][1]
            if all(res == first_result for _, res in exact_results):
                verification['all_exact_match'] = True
                verification['optimal_found'] = first_result
                
                # Check greedy
                greedy_res = algs['Greedy']['result']
                if isinstance(greedy_res, int):
                    if greedy_res == first_result:
                        verification['greedy_consistent'] = True
                        verification['notes'].append('Greedy found optimal solution')
                    else:
                        gap = ((first_result - greedy_res) / first_result * 100) if first_result > 0 else 0
                        verification['notes'].append(f'Greedy gap: {gap:.1f}%')
            else:
                verification['notes'].append('INCONSISTENCY: Exact algorithms disagree!')
                for name, res in exact_results:
                    verification['notes'].append(f'  {name}: {res}')
        
        return verification
    
    def run_tests(self, num_instances=100, max_per_size=3):
        """Run intensive test suite"""
        print('='*90)
        print('INTENSIVE 0/1 KNAPSACK ALGORITHM TEST SUITE')
        print('='*90)
        
        instances = self.find_test_instances(max_per_size=max_per_size)
        instances = instances[:num_instances]
        
        print(f'\nFound {len(instances)} test instances')
        print(f'Testing up to {num_instances} instances\n')
        
        self.total_tests = len(instances)
        
        # Test each instance
        for idx, instance in enumerate(instances, 1):
            result = self.test_single_instance(instance)
            self.results.append(result)
            
            # Print progress
            if result['verification']['all_exact_match']:
                self.passed_tests += 1
                status = '✓'
            else:
                self.failed_tests += 1
                status = '✗'
            
            if idx % 10 == 0 or idx <= 5:
                print(f'[{idx:3d}/{len(instances)}] {status} '
                      f'{result["category"]}/{result["size"]} '
                      f'n={result["n"]:5d} '
                      f'c={result["capacity"]:7d}')
        
        print(f'\n{"="*90}')
        print(f'TEST SUMMARY')
        print(f'{"="*90}')
        print(f'Total Tests:    {self.total_tests}')
        print(f'Passed:         {self.passed_tests} ({self.passed_tests/self.total_tests*100:.1f}%)')
        print(f'Failed:         {self.failed_tests}')
        
        return self.results
    
    def print_detailed_report(self, show_all=False):
        """Print detailed test results"""
        print(f'\n{"="*90}')
        print('DETAILED TEST RESULTS')
        print(f'{"="*90}\n')
        
        # Group by category
        by_category = {}
        for result in self.results:
            cat = result['category']
            if cat not in by_category:
                by_category[cat] = []
            by_category[cat].append(result)
        
        # Print results by category
        for category in sorted(by_category.keys()):
            results = by_category[category]
            passed = sum(1 for r in results if r['verification']['all_exact_match'])
            
            print(f'\n{category}:')
            print(f'  Tests: {len(results)}, Passed: {passed}, Failed: {len(results) - passed}')
            
            if show_all:
                for result in results[:3]:  # Show first 3 of each category
                    print(f'\n    {result["instance"]} (n={result["n"]}, c={result["capacity"]})')
                    algs = result['algorithms']
                    
                    for alg in ['BruteForce', 'Memoization', 'Tabulation', 'SpaceOptimised', 'Greedy']:
                        alg_data = algs[alg]
                        if alg_data['skipped']:
                            print(f'      {alg:20s}: SKIPPED')
                        elif isinstance(alg_data['result'], int):
                            time_str = f'{alg_data["time_ms"]:.4f}ms' if alg_data['time_ms'] else 'N/A'
                            print(f'      {alg:20s}: {alg_data["result"]:8d} ({time_str})')
                        else:
                            print(f'      {alg:20s}: {alg_data["result"]}')
        
        # Print inconsistencies
        print(f'\n{"="*90}')
        print('INCONSISTENCIES / FAILURES')
        print(f'{"="*90}\n')
        
        inconsistent = [r for r in self.results if not r['verification']['all_exact_match']]
        if inconsistent:
            print(f'Found {len(inconsistent)} inconsistencies:\n')
            for result in inconsistent[:10]:  # Show first 10
                print(f'  {result["instance"]} ({result["category"]}/{result["size"]}):')
                for note in result['verification']['notes']:
                    print(f'    {note}')
        else:
            print('✓ No inconsistencies found - All algorithms consistent!')
    
    def print_performance_analysis(self):
        """Analyze and print performance metrics"""
        print(f'\n{"="*90}')
        print('PERFORMANCE ANALYSIS')
        print(f'{"="*90}\n')
        
        # Collect timing data
        timings = {alg: [] for alg in ['BruteForce', 'Memoization', 'Tabulation', 'SpaceOptimised', 'Greedy']}
        
        for result in self.results:
            for alg in timings:
                alg_data = result['algorithms'][alg]
                if not alg_data['skipped'] and isinstance(alg_data['result'], int) and alg_data['time_ms']:
                    timings[alg].append(alg_data['time_ms'])
        
        print('Average Execution Times (milliseconds):')
        print('-' * 60)
        print(f'{"Algorithm":<20} {"Count":<8} {"Avg":<12} {"Min":<12} {"Max":<12}')
        print('-' * 60)
        
        for alg in ['BruteForce', 'Memoization', 'Tabulation', 'SpaceOptimised', 'Greedy']:
            times = timings[alg]
            if times:
                avg = sum(times) / len(times)
                min_t = min(times)
                max_t = max(times)
                print(f'{alg:<20} {len(times):<8} {avg:<12.6f} {min_t:<12.6f} {max_t:<12.6f}')
            else:
                print(f'{alg:<20} {"0":<8} {"SKIPPED":<12}')
        
        # Algorithm comparison
        print(f'\n{"="*90}')
        print('ALGORITHM COMPARISON (Relative to Tabulation)')
        print(f'{"="*90}\n')
        
        # Get average time for tabulation
        tab_times = timings['Tabulation']
        if tab_times:
            tab_avg = sum(tab_times) / len(tab_times)
            
            for alg in ['BruteForce', 'Memoization', 'SpaceOptimised', 'Greedy']:
                times = timings[alg]
                if times:
                    alg_avg = sum(times) / len(times)
                    ratio = alg_avg / tab_avg
                    print(f'{alg:20s}: {ratio:.2f}x {"FASTER" if ratio < 1 else "SLOWER"}')
    
    def save_results_csv(self, filename='test_results.csv'):
        """Save detailed results to CSV"""
        with open(filename, 'w', newline='') as f:
            writer = csv.writer(f)
            
            # Header
            writer.writerow([
                'Instance', 'Category', 'Size', 'Ratio', 'N', 'Capacity',
                'BruteForce_Result', 'BruteForce_Time_ms', 'BruteForce_Skipped',
                'Memoization_Result', 'Memoization_Time_ms', 'Memoization_Skipped',
                'Tabulation_Result', 'Tabulation_Time_ms', 'Tabulation_Items',
                'SpaceOptimised_Result', 'SpaceOptimised_Time_ms', 'SpaceOptimised_Skipped',
                'Greedy_Result', 'Greedy_Time_ms',
                'All_Match', 'Optimal', 'Verified'
            ])
            
            # Data rows
            for result in self.results:
                algs = result['algorithms']
                verify = result['verification']
                
                writer.writerow([
                    result['instance'],
                    result['category'],
                    result['size'],
                    result['ratio'],
                    result['n'],
                    result['capacity'],
                    
                    algs['BruteForce']['result'],
                    algs['BruteForce']['time_ms'],
                    algs['BruteForce']['skipped'],
                    
                    algs['Memoization']['result'],
                    algs['Memoization']['time_ms'],
                    algs['Memoization']['skipped'],
                    
                    algs['Tabulation']['result'],
                    algs['Tabulation']['time_ms'],
                    algs['Tabulation'].get('items', 0),
                    
                    algs['SpaceOptimised']['result'],
                    algs['SpaceOptimised']['time_ms'],
                    algs['SpaceOptimised']['skipped'],
                    
                    algs['Greedy']['result'],
                    algs['Greedy']['time_ms'],
                    
                    verify['all_exact_match'],
                    verify['optimal_found'],
                    len(verify['notes']) == 0 or (len(verify['notes']) == 1 and 'gap' in verify['notes'][0])
                ])
        
        print(f'\n✓ Results saved to {filename}')


def main():
    suite = TestSuite()
    
    # Run intensive tests
    print('\nStarting intensive test run...\n')
    suite.run_tests(num_instances=100, max_per_size=3)
    
    # Print reports
    suite.print_detailed_report(show_all=True)
    suite.print_performance_analysis()
    
    # Save results
    suite.save_results_csv()
    
    print(f'\n{"="*90}')
    print('TEST SUITE COMPLETE')
    print(f'{"="*90}\n')


if __name__ == '__main__':
    main()
