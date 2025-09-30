#!/usr/bin/env python3
"""Performance profiler for BRD transformer"""

import time
import cProfile
import pstats
from io import StringIO
from brd_transformer import BRDTransformer
import fitz

def profile_parsing():
    """Profile the BRD transformer performance"""

    # Load test document
    doc = fitz.open('/home/great/claudeprojects/parser/test_resumes/Test Resumes/Ahmad Qasem-Resume.pdf')
    text = ""
    for page in doc:
        text += page.get_text()
    doc.close()

    transformer = BRDTransformer()

    # Time individual components
    print("🔍 PERFORMANCE PROFILING")
    print("=" * 50)

    # Overall timing
    start_time = time.time()
    result = transformer.transform_to_brd_format(text, "test.pdf")
    total_time = (time.time() - start_time) * 1000

    print(f"Total processing time: {total_time:.2f}ms")
    print(f"Target time: 2ms")
    print(f"Performance gap: {total_time/2:.1f}x slower")

    # Profile with cProfile
    print("\n📊 DETAILED PROFILING:")
    pr = cProfile.Profile()
    pr.enable()

    # Run 10 times to get better stats
    for _ in range(10):
        transformer.transform_to_brd_format(text, "test.pdf")

    pr.disable()

    # Analyze results
    s = StringIO()
    ps = pstats.Stats(pr, stream=s).sort_stats('cumulative')
    ps.print_stats(20)  # Show top 20 functions

    print(s.getvalue())

if __name__ == "__main__":
    profile_parsing()