import type { Issue } from '@/types'

export interface RichIssueExplanation {
  detectedWhy: string
  dangerousWhy: string
  consequences: string
  bestPractice: string
  estimatedImpact: string
  problematicExplain: string
  improvedCode: string
  changesMade: string
  benefits: string
  standards: string
  difficulty: 'Easy' | 'Medium' | 'Hard'
  confidence: string
  additional: string
}

const EXPLANATIONS: Record<string, Partial<RichIssueExplanation>> = {
  // Python - SQL Injection
  'PYSec001': {
    detectedWhy: 'String concatenation or interpolation was detected inside a database query string.',
    dangerousWhy: 'Building SQL statements using string formatting allows attackers to manipulate database syntax by inputting malicious parameters (e.g. \x27 OR 1=1 --).',
    consequences: 'Complete database compromise, unauthorized data exposure, user deletion, or remote code execution.',
    bestPractice: 'Always use parameterized database libraries where the data is sent separately from the SQL statement parameters.',
    estimatedImpact: 'Security: Critical Risk | Performance: Neutral',
    problematicExplain: 'Directly injects the raw `username` and `role` variables into the SQL command buffer.',
    improvedCode: 'query = "SELECT * FROM users WHERE name = %s AND role = %s"\ncursor.execute(query, (username, role))',
    changesMade: 'Replaced `%` formatting with parameterized placeholder placeholders `%s` and passed variables in execute tuple.',
    benefits: 'Prevents SQL injection vulnerabilities entirely, improves database query cached query plans execution speed.',
    standards: 'CWE-89: SQL Injection, OWASP Top 10 A03: Injection, SEI CERT SEC01-PL',
    difficulty: 'Easy',
    confidence: '95%',
    additional: 'Implement strict input length validation and use ORM tools like SQLAlchemy.',
  },
  
  // Python - Hardcoded secret
  'PYSec003': {
    detectedWhy: 'A variable name matching patterns like key, secret, password or token was assigned a literal string value.',
    dangerousWhy: 'Storing passwords, api keys, or certificates directly in source code allows anyone with access to the repository to obtain high-privilege credentials.',
    consequences: 'Production service compromise, data breach, credentials leak on public git providers (e.g. GitHub).',
    bestPractice: 'Load secrets dynamically from environment variables or a secure local credentials vault at runtime.',
    estimatedImpact: 'Security: Critical Risk | Maintainability: High',
    problematicExplain: 'Stores a hardcoded admin password literal string inside the code.',
    improvedCode: 'import os\nSECRET_KEY = os.environ.get("SECRET_KEY", "fallback_safe_default")',
    changesMade: 'Replaced hardcoded literal password with an environment variable lookup check.',
    benefits: 'Prevents credential leaks, makes project deployment configuration dynamic.',
    standards: 'CWE-798: Use of Hardcoded Credentials, OWASP Top 10 A02: Cryptographic Failures',
    difficulty: 'Easy',
    confidence: '90%',
    additional: 'Setup repository pre-commit hooks to scan and reject commits with keys.',
  },
  
  // Python - eval usage
  'PYSec002': {
    detectedWhy: 'The built-in `eval()` function was called on dynamic parameters.',
    dangerousWhy: 'The `eval()` function compiles and runs arbitrary text blocks as python statements, allowing attackers to execute commands.',
    consequences: 'Arbitrary shell command execution, process hijack, host system compromises.',
    bestPractice: 'Use safe serializers like `json.loads()` or lookups maps instead of evaluating code.',
    estimatedImpact: 'Security: Critical Risk | Readability: Low',
    problematicExplain: 'Calls dynamic execution parser on untrusted arguments.',
    improvedCode: 'import json\nresult = json.loads(username)',
    changesMade: 'Switched dynamic evaluation string parsing to safe json parser execution.',
    benefits: 'Fully blocks host system execution vulnerability path.',
    standards: 'CWE-95: Eval Injection, OWASP Top 10 A03: Injection',
    difficulty: 'Medium',
    confidence: '95%',
    additional: 'Avoid any execution of dynamic strings.',
  },

  // JS - var usage
  'JS001': {
    detectedWhy: 'Variable declared using the obsolete `var` keyword.',
    dangerousWhy: 'The `var` keyword has function-scope instead of block-scope, which leads to hoisting issues and subtle reassignment bugs.',
    consequences: 'Scope pollution, unexpected null dereferences, variables hoisting collision bugs.',
    bestPractice: 'Use `let` for variables that will be reassigned, and `const` for immutable variables.',
    estimatedImpact: 'Readability: High | Maintainability: High',
    problematicExplain: 'Declares variable scoped globally or function-wide.',
    improvedCode: 'const port = 3000;\nlet active = true;',
    changesMade: 'Replaced `var` declarations with block-scoped `const` and `let` qualifiers.',
    benefits: 'Clean code scoping, matches ECMAScript 6+ standard development rules.',
    standards: 'ESLint Rule: no-var, JS best practices guide',
    difficulty: 'Easy',
    confidence: '98%',
    additional: 'Configure typescript strict compiler options.',
  },

  // JS - console.log
  'JS003': {
    detectedWhy: 'Active call to `console.log()` detected.',
    dangerousWhy: 'Leftover debugging lines leak system logs, internal variables, and clutter build pipelines.',
    consequences: 'Diagnostic logs leaking, performance overhead on verbose terminal writes.',
    bestPractice: 'Use proper logging frameworks (Winston, Loguru) or remove debug log statements.',
    estimatedImpact: 'Readability: Medium | Performance: Low',
    problematicExplain: 'Prints variable values to general stdout terminal.',
    improvedCode: '// Logger.info("Server started");',
    changesMade: 'Removed console print calls in production execution scope.',
    benefits: 'Prevents standard logging spam, improves performance.',
    standards: 'ESLint Rule: no-console',
    difficulty: 'Easy',
    confidence: '95%',
    additional: 'Enforce pre-production linters check.',
  },

  // JS - Loose equality ==
  'JS002': {
    detectedWhy: 'Loose comparison `==` used instead of strict `===`.',
    dangerousWhy: 'Loose equality performs implicit type coercion, leading to false positives (e.g. 0 == false is true).',
    consequences: 'Logic branching bypass, runtime parsing exception bugs.',
    bestPractice: 'Always use strict equality `===` comparisons.',
    estimatedImpact: 'Readability: High | Maintainability: High',
    problematicExplain: 'Compares boolean state using loose integer mapping.',
    improvedCode: 'if (active === true) {',
    changesMade: 'Replaced `==` with `===` strict equality validation.',
    benefits: 'Enforces type safety in condition checks.',
    standards: 'CWE-595: Comparison of Object References, JS Guide',
    difficulty: 'Easy',
    confidence: '95%',
    additional: 'Apply strict compiler modes.',
  },

  // C - gets usage
  'CSec001': {
    detectedWhy: 'Usage of the unsafe standard input reader `gets()` was detected.',
    dangerousWhy: 'The `gets()` function does not check buffer limits, writing input bytes continuously, making it vulnerable to stack buffer overflows.',
    consequences: 'Stack corruption, program crash, remote control system hijack.',
    bestPractice: 'Use `fgets()` which limits the maximum number of characters copied to the buffer.',
    estimatedImpact: 'Security: Critical Risk | Reliability: High',
    problematicExplain: 'Reads string input to fixed buffer without boundary checks.',
    improvedCode: 'fgets(buf, sizeof(buf), stdin);',
    changesMade: 'Replaced `gets` with `fgets` including buffer limit bounds constraint.',
    benefits: 'Eliminates stack buffer overflow risk path.',
    standards: 'CWE-120: Buffer Overflow, OWASP TOP 10 A06: Vulnerable Components, CERT MSC24-C',
    difficulty: 'Easy',
    confidence: '99%',
    additional: 'Avoid any use of outdated standard string copy macros.',
  },

  // SQL - SELECT *
  'SQL001': {
    detectedWhy: 'SELECT * was used in a database query statement.',
    dangerousWhy: 'Fetching all columns increases network payload, uses unnecessary I/O, and causes application failures if table schema column order changes.',
    consequences: 'Slow SQL response, high memory overhead, database connection saturation.',
    bestPractice: 'Select only the specific column attributes required by the logic.',
    estimatedImpact: 'Performance: High | Maintainability: High',
    problematicExplain: 'Fetches all database columns from users table.',
    improvedCode: 'SELECT id, username, email FROM users WHERE active = 1;',
    changesMade: 'Specified actual attributes required instead of asterisk wildcard.',
    benefits: 'Reduces database query payload size, improves query index lookup plan speeds.',
    standards: 'SQL Performance Guide, database access best practices',
    difficulty: 'Easy',
    confidence: '95%',
    additional: 'Use projection limits in SQL queries.',
  },

  // SQL - GRANT ALL
  'SQLSec002': {
    detectedWhy: 'GRANT ALL privileges statement found in database schema scripts.',
    dangerousWhy: 'Granting all privileges to database accounts violates the principle of least privilege.',
    consequences: 'Privilege escalation risks, full table database drop risks by compromised users.',
    bestPractice: 'Grant only minimum permission scopes required (e.g. SELECT, INSERT).',
    estimatedImpact: 'Security: High | Maintainability: High',
    problematicExplain: 'Grants root accounts unrestricted access parameters.',
    improvedCode: 'GRANT SELECT, INSERT, UPDATE ON database_development.* TO \'root\'@\'localhost\';',
    changesMade: 'Replaced wildcard privileges with strict permission list.',
    benefits: 'Restricts permissions to required subsets.',
    standards: 'CWE-272: Least Privilege Violation, OWASP Top 10 A05: Security Misconfiguration',
    difficulty: 'Easy',
    confidence: '90%',
    additional: 'Perform continuous database accounts audits.',
  }
}

export function getDetailedExplanation(issue: Issue, language: string): RichIssueExplanation {
  const defaults: RichIssueExplanation = {
    detectedWhy: 'This code pattern matches a static rule checker signature in the local review registry.',
    dangerousWhy: 'Unresolved code smells and warnings may accumulate technical debt, affect code readability, or introduce logical flaws over time.',
    consequences: 'Decreased codebase maintainability, difficult regression testing, and higher probability of bugs.',
    bestPractice: 'Adopt modern clean-coding guidelines, decouple classes, and format according to standards.',
    estimatedImpact: 'Maintainability: Low | Readability: Medium',
    problematicExplain: `Problematic syntax code fragment: \x60${issue.code_snippet || 'at line ' + issue.line_number}\x60`,
    improvedCode: '// Refactoring required for this code snippet.',
    changesMade: 'Review code structure and apply standard formatting rules.',
    benefits: 'Improves software modularity, readability, and overall quality scores.',
    standards: 'Language-specific coding standards (PEP-8, ESLint, Google Style Guide)',
    difficulty: 'Easy',
    confidence: '85%',
    additional: 'Perform comprehensive team review and run automated linters.',
  }

  const lookup = EXPLANATIONS[issue.rule_id] || {}
  
  // Try mapping by matching substring titles if rule_id not found directly
  if (Object.keys(lookup).length === 0) {
    if (issue.title.includes('eval')) {
      return { ...defaults, ...EXPLANATIONS['PYSec002'] } as RichIssueExplanation
    }
    if (issue.title.includes('Credential') || issue.title.includes('password')) {
      return { ...defaults, ...EXPLANATIONS['PYSec003'] } as RichIssueExplanation
    }
    if (issue.title.includes('SELECT *')) {
      return { ...defaults, ...EXPLANATIONS['SQL001'] } as RichIssueExplanation
    }
    if (issue.title.includes('gets')) {
      return { ...defaults, ...EXPLANATIONS['CSec001'] } as RichIssueExplanation
    }
  }

  return {
    ...defaults,
    ...lookup,
  } as RichIssueExplanation
}
