#!/usr/bin/env python3
"""
Command-line interface for Resume Parser
Allows parsing resumes without using the Streamlit UI
"""

import argparse
import json
import sys
from pathlib import Path
from resume_parser import NLPResumeParser, batch_parse_resumes, get_file_text
import os
from dotenv import load_dotenv


def main():
    """Main CLI function"""
    load_dotenv()
    
    parser = argparse.ArgumentParser(
        description='Resume Parser - Extract structured data from resumes using NLP',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Parse a single resume
  python cli.py --file resume.pdf
  
  # Batch process multiple resumes
  python cli.py --batch resumes_folder/ --output results.json
  
  # Parse and save to file
  python cli.py --file resume.txt --output result.json
  
  # Parse with caching disabled
  python cli.py --file resume.txt --no-cache
        """
    )
    
    parser.add_argument(
        '--file', '-f',
        help='Path to resume file (TXT, PDF, or DOCX)',
        type=str
    )
    
    parser.add_argument(
        '--batch', '-b',
        help='Process all resumes in a folder',
        type=str
    )
    
    parser.add_argument(
        '--output', '-o',
        help='Output file path for results (JSON format)',
        type=str
    )
    
    parser.add_argument(
        '--no-cache',
        help='Disable caching of results',
        action='store_true'
    )
    
    parser.add_argument(
        '--verbose', '-v',
        help='Enable verbose output',
        action='store_true'
    )
    
    args = parser.parse_args()
    
    # Validate arguments
    if not args.file and not args.batch:
        parser.print_help()
        print("\n❌ Error: Please specify either --file or --batch")
        sys.exit(1)
    
    try:
        # Single file processing
        if args.file:
            if not Path(args.file).exists():
                print(f"❌ Error: File not found: {args.file}")
                sys.exit(1)
            
            if args.verbose:
                print(f"📄 Parsing: {args.file}")
            
            parse_single_file(args.file, args.output, args.no_cache, args.verbose)
        
        # Batch processing
        elif args.batch:
            if not Path(args.batch).is_dir():
                print(f"❌ Error: Directory not found: {args.batch}")
                sys.exit(1)
            
            if args.verbose:
                print(f"📦 Batch processing directory: {args.batch}")
            
            parse_batch(args.batch, args.output, args.no_cache, args.verbose)
    
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        sys.exit(1)


def parse_single_file(file_path, output_file, no_cache, verbose):
    """Parse a single resume file"""
    try:
        # Initialize parser
        resume_parser = NLPResumeParser(use_cache=not no_cache)
        
        # Parse file
        result = resume_parser.parse_from_file(file_path)
        
        # Display results
        if verbose:
            print("\n✅ Parsing successful!\n")
        
        display_result(result)
        
        # Save to file if specified
        if output_file:
            with open(output_file, 'w') as f:
                json.dump(result, f, indent=2)
            print(f"\n💾 Results saved to: {output_file}")
        
    except Exception as e:
        raise Exception(f"Failed to parse {file_path}: {str(e)}")


def parse_batch(batch_dir, output_file, no_cache, verbose):
    """Batch process resumes in a directory"""
    try:
        output_path = output_file or "batch_results.json"
        
        # Use batch processing function
        results = batch_parse_resumes(batch_dir, output_file=output_path)
        
        # Summary
        success_count = sum(1 for r in results if r.get('success'))
        total_count = len(results)
        
        print(f"\n✅ Batch processing complete!")
        print(f"   Total: {total_count} | Success: {success_count} | Failed: {total_count - success_count}")
        print(f"   Results saved to: {output_path}")
        
        # Show failures if any
        failed = [r for r in results if not r.get('success')]
        if failed and verbose:
            print("\n⚠️  Failed files:")
            for f in failed:
                print(f"   - {f['filename']}: {f.get('error')}")
    
    except Exception as e:
        raise Exception(f"Batch processing failed: {str(e)}")


def display_result(result):
    """Display parsed resume in formatted way"""
    print("=" * 60)
    print("RESUME PARSING RESULTS")
    print("=" * 60)
    
    # Personal Information
    print("\n📋 PERSONAL INFORMATION")
    print("-" * 60)
    print(f"Name:        {result.get('name') or 'N/A'}")
    print(f"Email:       {result.get('email') or 'N/A'}")
    print(f"Phone:       {result.get('phone') or 'N/A'}")
    print(f"Position:    {result.get('position') or 'N/A'}")
    print(f"Experience:  {result.get('experience') or 'N/A'}")
    print(f"Education:   {result.get('education') or 'N/A'}")
    
    # Summary
    if result.get('summary'):
        print("\n📝 PROFESSIONAL SUMMARY")
        print("-" * 60)
        print(result['summary'])
    
    # Skills
    print("\n🎯 SKILLS")
    print("-" * 60)
    
    primary = result.get('primarySkills', [])
    if primary:
        print("Primary Skills (Core Competencies):")
        for skill in primary:
            print(f"  • {skill}")
    
    secondary = result.get('secondarySkills', [])
    if secondary:
        print("\nSecondary Skills (Supporting):")
        for skill in secondary:
            print(f"  • {skill}")
    
    # Skills source
    if result.get('skillsSource'):
        print("\n📊 SKILLS DETERMINATION")
        print("-" * 60)
        print(result['skillsSource'])
    
    print("\n" + "=" * 60)
    print("📋 Complete JSON output:")
    print("=" * 60)
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
