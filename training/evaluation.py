from transformers import pipeline
import time
from typing import List, Dict

class ModelEvaluator:
    def __init__(self, model_path: str):
        self.model = pipeline('text-generation', model=model_path)
    def evaluate_command_generation(self, test_cases: List[Dict]) -> Dict:
        results = {
            'total_tests': len(test_cases),
            'successful_commands': 0,
            'average_response_time': 0,
            'command_accuracy': 0
        }
        total_time = 0
        for test_case in test_cases:
            start_time = time.time()
            response = self.model(test_case['input'], max_length=512)
            end_time = time.time()
            total_time += (end_time - start_time)
            if test_case['expected_command'] in response[0]['generated_text']:
                results['successful_commands'] += 1
        results['average_response_time'] = total_time / len(test_cases)
        results['command_accuracy'] = results['successful_commands'] / len(test_cases)
        return results 